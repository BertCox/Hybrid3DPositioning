/*
 * Copyright (c) 2019, Texas Instruments Incorporated
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * *  Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 * *  Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * *  Neither the name of Texas Instruments Incorporated nor the names of
 *    its contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
 * OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
 * OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
 * EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

/***** Includes *****/
/* Standard C Libraries */
#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <stddef.h>



/* TI Drivers */
#include <ti/drivers/rf/RF.h>
#include <ti/drivers/PIN.h>
#include <ti/drivers/pin/PINCC26XX.h>
#include <xdc/runtime/System.h>


/* Driverlib Header files */
#include DeviceFamily_constructPath(driverlib/rf_prop_mailbox.h)

/* Board Header files */
#include "Board.h"

/* Application Header files */
#include "RFQueue.h"
#include "smartrf_settings/smartrf_settings.h"

/* Sensor Controller files */

#include <xdc/runtime/System.h>
#include "scif.h"
#define BV(x) (1 << (x))


/* Driver Header files */
#include <ti/drivers/GPIO.h>


/***** Defines *****/

/* Do power measurement */
#define POWER_MEASUREMENT

#define CHIRPDATASIZE  480
#define SAMPLEDATASIZE 16
#define SAMPLEBITSIZE  512
#define WORDSIZE       32
#define CHIRPDATAPAIRS (CHIRPDATASIZE/SAMPLEDATASIZE)
#define TRANSMITTER_ID 32133

uint16_t sampleData[WORDSIZE];
static uint16_t receivedTransmitterID = 0;

/* Packet RX Configuration */
#define PAYLOAD_LENGTH_RX         2


/* Packet TX Configuration */
#define PAYLOAD_LENGTH      SAMPLEDATASIZE*4+2 // long is 4 bytes + 2 bytes for Sequence Number
#ifdef POWER_MEASUREMENT
#define PACKET_INTERVAL     1  /* For power measurement set packet interval to 5s */
#else
#define PACKET_INTERVAL     1  /* Set packet interval to 500000us or 500ms */
#endif

/* Set Transmit (echo) delay to 1ms */
#define TX_DELAY             (uint32_t)(4000000*0.001f)
#define NUM_DATA_ENTRIES       2
/* The Data Entries data field will contain:
 * 1 Header byte (RF_cmdPropRx.rxConf.bIncludeHdr = 0x1)
 * Max 30 payload bytes
 * 1 status byte (RF_cmdPropRx.rxConf.bAppendStatus = 0x1) */
#define NUM_APPENDED_BYTES     2

/***** Prototypes *****/
static void echoCallback(RF_Handle h, RF_CmdHandle ch, RF_EventMask e);


/***** Variable declarations *****/
static RF_Object rfObject;
static RF_Handle rfHandle;

/* Pin driver handle */
static PIN_Handle ledPinHandle;
static PIN_State ledPinState;
static PIN_Handle gpioPinHandle; //ledPinHandle
static PIN_State gpioPinState;   //ledPinState

static uint8_t txpacket[PAYLOAD_LENGTH];
static uint16_t seqNumber;

#if defined(__TI_COMPILER_VERSION__)
#pragma DATA_ALIGN(rxDataEntryBuffer, 4)
static uint8_t
rxDataEntryBuffer[RF_QUEUE_DATA_ENTRY_BUFFER_SIZE(NUM_DATA_ENTRIES,
                                                  PAYLOAD_LENGTH,
                                                  NUM_APPENDED_BYTES)];
#elif defined(__IAR_SYSTEMS_ICC__)
#pragma data_alignment = 4
static uint8_t
rxDataEntryBuffer[RF_QUEUE_DATA_ENTRY_BUFFER_SIZE(NUM_DATA_ENTRIES,
                                                  PAYLOAD_LENGTH,
                                                  NUM_APPENDED_BYTES)];
#elif defined(__GNUC__)
static uint8_t
rxDataEntryBuffer[RF_QUEUE_DATA_ENTRY_BUFFER_SIZE(NUM_DATA_ENTRIES,
                                                  PAYLOAD_LENGTH,
                                                  NUM_APPENDED_BYTES)]
                                                  __attribute__((aligned(4)));
#else
#error This compiler is not supported
#endif //defined(__TI_COMPILER_VERSION__)

/* Receive Statistics */
static rfc_propRxOutput_t rxStatistics;

/* Receive dataQueue for RF Core to fill in data */
static dataQueue_t dataQueue;
static rfc_dataEntryGeneral_t* currentDataEntry;
static uint8_t packetLength;
static uint8_t i = 0;
static uint8_t* packetDataPointer;
static bool sleepOk = false;

/*
 * Application LED pin configuration table:
 *   - All LEDs board LEDs are off.
 */
PIN_Config pinTable[] =
{
    Board_PIN_LED1 | PIN_GPIO_OUTPUT_EN | PIN_GPIO_LOW | PIN_PUSHPULL | PIN_DRVSTR_MAX,
    Board_PIN_LED2 | PIN_GPIO_OUTPUT_EN | PIN_GPIO_LOW | PIN_PUSHPULL | PIN_DRVSTR_MAX,
#ifdef POWER_MEASUREMENT
#if defined(Board_CC1350_LAUNCHXL)
    Board_DIO30_SWPWR | PIN_GPIO_OUTPUT_EN | PIN_GPIO_HIGH | PIN_PUSHPULL | PIN_DRVSTR_MAX,
#endif
#endif
    PIN_TERMINATE
};

PIN_Config GPIOpinTable[] =
{
 Board_DIO21 | PIN_GPIO_OUTPUT_EN | PIN_GPIO_LOW | PIN_PUSHPULL | PIN_DRVSTR_MAX,
 Board_DIO22 | PIN_GPIO_OUTPUT_EN | PIN_GPIO_LOW | PIN_PUSHPULL | PIN_DRVSTR_MAX,
    PIN_TERMINATE
};

/***** Function definitions *****/

/*
 *  ======== Callback from alert of SC ========
 */
void scTaskAlertCallback(void)
{
    scifClearAlertIntSource();


    PIN_setOutputValue(gpioPinHandle, Board_DIO22, 0);
    for(i = 0; i< WORDSIZE; i++){
            sampleData[i]= scifTaskData.binarySampling.output.outputArray[i];
    }

//
//    PIN_setOutputValue(gpioPinHandle, Board_DIO21, 1);
//    PIN_setOutputValue(gpioPinHandle, Board_DIO21, 0);
//    PIN_setOutputValue(gpioPinHandle, Board_DIO21, 1);
//    PIN_setOutputValue(gpioPinHandle, Board_DIO21, 0);
//    System_printf("Interrupt \n");
//    System_flush();

    // Acknowledge the ALERT event
    scifAckAlertEvents();
} // scCtrlReadyCallback




/*
 *  ======== mainThread ========
 */
void *mainThread(void *arg0)
{
    RF_Params rfParams;
    RF_Params_init(&rfParams);

    /* Open LED pins */
    ledPinHandle = PIN_open(&ledPinState, pinTable);
    if (ledPinHandle == NULL)
    {
        while(1);
    }

    gpioPinHandle = PIN_open(&gpioPinState, GPIOpinTable);
    if (gpioPinHandle == NULL)
    {
        while(1);
    }

    /* Call driver init functions */
    GPIO_init();
    PIN_setOutputValue(gpioPinHandle, Board_DIO21, 0);
    PIN_setOutputValue(gpioPinHandle, Board_DIO22, 0);


    /* Sensor Controller Initialization */
    scifOsalInit();
    scifOsalRegisterTaskAlertCallback(scTaskAlertCallback);
    scifInit(&scifDriverSetup);
    scifStartTasksNbl(BV(SCIF_BINARY_SAMPLING_TASK_ID));

#ifdef POWER_MEASUREMENT
#if defined(Board_CC1350_LAUNCHXL)
    /* Route out PA active pin to Board_DIO30_SWPWR */
    PINCC26XX_setMux(ledPinHandle, Board_DIO30_SWPWR, PINCC26XX_MUX_RFC_GPO1);
#endif
#endif


    if( RFQueue_defineQueue(&dataQueue,
                                rxDataEntryBuffer,
                                sizeof(rxDataEntryBuffer),
                                NUM_DATA_ENTRIES,
                                PAYLOAD_LENGTH_RX + NUM_APPENDED_BYTES))
        {
            #ifndef POWER_MEASUREMENT
                /* Failed to allocate space for all data entries */
                PIN_setOutputValue(ledPinHandle, Board_PIN_LED1, 1);
                PIN_setOutputValue(ledPinHandle, Board_PIN_LED2, 1);
            #endif

            while(1);
        }


    /* Modify CMD_PROP_TX and CMD_PROP_RX commands for application needs */
        /* Set the Data Entity queue for received data */
        RF_cmdPropRx.pQueue = &dataQueue;
        /* Discard ignored packets from Rx queue */
        RF_cmdPropRx.rxConf.bAutoFlushIgnored = 1;
        /* Discard packets with CRC error from Rx queue */
        RF_cmdPropRx.rxConf.bAutoFlushCrcErr = 1;
        /* Implement packet length filtering to avoid PROP_ERROR_RXBUF */
        RF_cmdPropRx.maxPktLen = PAYLOAD_LENGTH_RX;
        /* End RX operation when a packet is received correctly and move on to the
         * next command in the chain */
        RF_cmdPropRx.pktConf.bRepeatOk = 0;
        RF_cmdPropRx.pktConf.bRepeatNok = 1;
        RF_cmdPropRx.startTrigger.triggerType = TRIG_NOW;
        RF_cmdPropRx.pNextOp = (rfc_radioOp_t *)&RF_cmdPropTx;
        /* Only run the TX command if RX is successful */
        RF_cmdPropRx.condition.rule = COND_STOP_ON_FALSE;
        RF_cmdPropRx.pOutput = (uint8_t *)&rxStatistics;

        RF_cmdPropTx.pktLen = PAYLOAD_LENGTH;
        RF_cmdPropTx.pPkt = txpacket;
        RF_cmdPropTx.startTrigger.triggerType = TRIG_REL_PREVEND;
        RF_cmdPropTx.startTime = TX_DELAY;


    /* Request access to the radio */
#if defined(DeviceFamily_CC26X0R2)
    rfHandle = RF_open(&rfObject, &RF_prop, (RF_RadioSetup*)&RF_cmdPropRadioSetup, &rfParams);
#else
    rfHandle = RF_open(&rfObject, &RF_prop, (RF_RadioSetup*)&RF_cmdPropRadioDivSetup, &rfParams);
#endif// DeviceFamily_CC26X0R2

    /* Set the frequency */
    RF_postCmd(rfHandle, (RF_Op*)&RF_cmdFs, RF_PriorityNormal, NULL, 0);

    while(1)
        {
            /* Wait for a packet
             * - When the first of the two chained commands (RX) completes, the
             * RF_EventCmdDone and RF_EventRxEntryDone events are raised on a
             * successful packet reception, and then the next command in the chain
             * (TX) is run
             * - If the RF core runs into an issue after receiving the packet
             * incorrectly onlt the RF_EventCmdDone event is raised; this is an
             * error condition
             * - If the RF core successfully echos the received packet the RF core
             * should raise the RF_EventLastCmdDone event
             */
            RF_EventMask terminationReason =
                    RF_runCmd(rfHandle, (RF_Op*)&RF_cmdPropRx, RF_PriorityNormal,
                              echoCallback, (RF_EventRxEntryDone |
                              RF_EventLastCmdDone));

            switch(terminationReason)
            {
                case RF_EventLastCmdDone:
                    // A stand-alone radio operation command or the last radio
                    // operation command in a chain finished.
                    break;
                case RF_EventCmdCancelled:
                    // Command cancelled before it was started; it can be caused
                    // by RF_cancelCmd() or RF_flushCmd().
                    break;
                case RF_EventCmdAborted:
                    // Abrupt command termination caused by RF_cancelCmd() or
                    // RF_flushCmd().
                    break;
                case RF_EventCmdStopped:
                    // Graceful command termination caused by RF_cancelCmd() or
                    // RF_flushCmd().
                    break;
                default:
                    // Uncaught error event
                    while(1);
            }

            uint32_t cmdStatus = ((volatile RF_Op*)&RF_cmdPropRx)->status;
            switch(cmdStatus)
            {
                case PROP_DONE_OK:
                    // Packet received with CRC OK
                    break;
                case PROP_DONE_RXERR:
                    // Packet received with CRC error
                    break;
                case PROP_DONE_RXTIMEOUT:
                    // Observed end trigger while in sync search
                    break;
                case PROP_DONE_BREAK:
                    // Observed end trigger while receiving packet when the command is
                    // configured with endType set to 1
                    break;
                case PROP_DONE_ENDED:
                    // Received packet after having observed the end trigger; if the
                    // command is configured with endType set to 0, the end trigger
                    // will not terminate an ongoing reception
                    break;
                case PROP_DONE_STOPPED:
                    // received CMD_STOP after command started and, if sync found,
                    // packet is received
                    break;
                case PROP_DONE_ABORT:
                    // Received CMD_ABORT after command started
                    break;
                case PROP_ERROR_RXBUF:
                    // No RX buffer large enough for the received data available at
                    // the start of a packet
                    break;
                case PROP_ERROR_RXFULL:
                    // Out of RX buffer space during reception in a partial read
                    break;
                case PROP_ERROR_PAR:
                    // Observed illegal parameter
                    break;
                case PROP_ERROR_NO_SETUP:
                    // Command sent without setting up the radio in a supported
                    // mode using CMD_PROP_RADIO_SETUP or CMD_RADIO_SETUP
                    break;
                case PROP_ERROR_NO_FS:
                    // Command sent without the synthesizer being programmed
                    break;
                case PROP_ERROR_RXOVF:
                    // RX overflow observed during operation
                    break;
                default:
                    // Uncaught error event - these could come from the
                    // pool of states defined in rf_mailbox.h
                    while(1);
            }
            if(sleepOk){
                sleepOk = false;
                RF_yield(rfHandle);
                usleep(960000);
            }
        }

}



static void echoCallback(RF_Handle h, RF_CmdHandle ch, RF_EventMask e)
{
#ifdef LOG_RADIO_EVENTS
    eventLog[evIndex++ & 0x1F] = e;
#endif// LOG_RADIO_EVENTS

    if (e & RF_EventRxEntryDone)
    { /* Start sampling*/
        PIN_setOutputValue(gpioPinHandle, Board_DIO22, 1);
        PIN_setOutputValue(gpioPinHandle, Board_DIO22, 0);

//        PIN_setOutputValue(gpioPinHandle, Board_DIO21, 1);
//        PIN_setOutputValue(gpioPinHandle, Board_DIO21, 0);
//        PIN_setOutputValue(gpioPinHandle, Board_DIO21, 1);
//        PIN_setOutputValue(gpioPinHandle, Board_DIO21, 0);
//        PIN_setOutputValue(gpioPinHandle, Board_DIO21, 1);
//        PIN_setOutputValue(gpioPinHandle, Board_DIO21, 0);
        /* Successful RX */

        #ifndef POWER_MEASUREMENT
            /* Toggle LED2, clear LED1 to indicate RX */
            PIN_setOutputValue(ledPinHandle, Board_PIN_LED1, 0);
            PIN_setOutputValue(ledPinHandle, Board_PIN_LED2,
                           !PIN_getOutputValue(Board_PIN_LED2));
        #endif


        /* Get current unhandled data entry */
        currentDataEntry = RFQueue_getDataEntry();

        /* Handle the packet data, located at &currentDataEntry->data:
         * - Length is the first byte with the current configuration
         * - Data starts from the second byte */
        packetLength      = *(uint8_t *)(&(currentDataEntry->data));
        packetDataPointer = (uint8_t *)(&(currentDataEntry->data) + 1);

        /* Copy the payload + status byte to the rxPacket variable, and then
         * over to the txPacket
         */

        /*check if the Received data equals the TRANSMITTER_ID*/
        receivedTransmitterID = ((unsigned int)packetDataPointer[0] << 8) | packetDataPointer[1];
        if( receivedTransmitterID == TRANSMITTER_ID ) {

            #ifndef POWER_MEASUREMENT
                System_printf("Transmitter ID correct \n");
                System_flush();
                PIN_setOutputValue(gpioPinHandle, Board_DIO21, 1);
                PIN_setOutputValue(gpioPinHandle, Board_DIO21, 0);
            #endif


            /* Create packet with incrementing sequence number */
                    txpacket[0] = (uint8_t)(seqNumber >> 8);
                    txpacket[1] = (uint8_t)(seqNumber++);
                    uint8_t i;
                    uint8_t j;
                    for (i = 2; i < PAYLOAD_LENGTH; i=i+2)
                    {
                        j = (i-2)/2;
                        txpacket[i] = (uint8_t)((sampleData[j])>> 8);
                        txpacket[(i+1)] = (uint8_t)((sampleData[j]));
                    }
        }


//        System_printf("Sample data: \n");
//        for(int uvw = 2; uvw< PAYLOAD_LENGTH; uvw++){
//           System_printf(" %u " , txpacket[uvw]);
//        }

//        System_printf("\n RX Correct \n");
//        System_flush();
        RFQueue_nextEntry();
    }
    else if (e & RF_EventLastCmdDone)
    {
        /* Successful Echo (TX)*/
        /* Toggle LED2, clear LED1 to indicate RX */
//        System_printf("Tx Correct \n");
//        System_flush();
        #ifndef POWER_MEASUREMENT
        PIN_setOutputValue(ledPinHandle, Board_PIN_LED1, 0);
        PIN_setOutputValue(ledPinHandle, Board_PIN_LED2,
                           !PIN_getOutputValue(Board_PIN_LED2));
        #endif
        sleepOk = true;

    }
    else // any uncaught event
    {
        #ifndef POWER_MEASUREMENT
            System_printf("AN ERROR OCCURED \n");
            System_flush();
            /* Error Condition: set LED1, clear LED2 */
                PIN_setOutputValue(ledPinHandle, Board_PIN_LED1, 1);
                PIN_setOutputValue(ledPinHandle, Board_PIN_LED2, 0);
        #endif

    }
}
