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

/* TI Drivers */
#include <ti/drivers/rf/RF.h>
#include <ti/drivers/PIN.h>
#include <ti/drivers/Power.h>
#include <ti/drivers/power/PowerCC26XX.h>
#include <ti/drivers/timer/GPTimerCC26XX.h>
#include <ti/sysbios/BIOS.h>
#include <ti/sysbios/knl/Task.h>
#include <xdc/runtime/System.h>
#include <ti/display/Display.h>
#include "UARTUtils.h"

/* high-accuracy clock */
Power_setDependency(PowerCC20XX_XOSC_HF);

/* Driverlib Header files */
#include DeviceFamily_constructPath(driverlib/rf_prop_mailbox.h)

/* Board Header files */
#include "Board.h"

/* Application Header files */
#include "RFQueue.h"
#include "smartrf_settings/smartrf_settings.h"

/****************************** Defines ****************************/

/*Sample Data*/
#define CHIRPDATASIZE  480
#define SAMPLEDATASIZE 16
#define SAMPLEBITSIZE  512
#define WORDSIZE       32
#define CHIRPDATAPAIRS (CHIRPDATASIZE/SAMPLEDATASIZE)

/*Randomly chosen Transmitter ID*/
#define TRANSMITTER_ID 32133

/* Packet RX Configuration */
#define DATA_ENTRY_HEADER_SIZE 8  /* Constant header size of a Generic Data Entry */
#define MAX_LENGTH             SAMPLEDATASIZE*4+2 /* Max length byte the radio will accept */
#define NUM_DATA_ENTRIES       2  /* NOTE: Only two data entries supported at the moment */
#define NUM_APPENDED_BYTES     2  /* The Data Entries data field will contain:
                                   * 1 Header byte (RF_cmdPropRx.rxConf.bIncludeHdr = 0x1)
                                   * Max 30 payload bytes
                                   * 1 status byte (RF_cmdPropRx.rxConf.bAppendStatus = 0x1) */

/* Packet TX Configuration */
#define PAYLOAD_LENGTH      2
/* Set packet interval to 30ms */
#define PACKET_INTERVAL     (uint32_t)(4000000*0.02637f)
/* Set Receive timeout to 50ms */
#define RX_TIMEOUT          (uint32_t)(4000000*0.05f)


/* Log radio events in the callback */
//#define LOG_RADIO_EVENTS

/*************************** Variables ****************************/


static unsigned long packetADC[SAMPLEDATASIZE]; // The length byte is stored in a separate variable
const unsigned long mask = 0x80000000;          // Masking to get the highest bit
static uint32_t curtime;

static bool rfTransmission = false;
double distance = 0;

 unsigned long referenceDataChirp[CHIRPDATASIZE];


  unsigned long dataChirp[CHIRPDATASIZE] =
  {
   3766226881, 4164880352, 4228874736, 1040703740, 528740414, 130087967,
   2213576199, 3237486467, 4034791360, 4162814960, 2114437372, 528740414,
   130087967, 2180005383, 3774615425, 4164880352, 2081407480, 520351870,
   264304671, 2213559815, 3774615425, 4164879328, 2114961656, 528609343,
   132152335, 3254263555, 4030597088, 4228874744, 520351870, 132185103,
   2180521731, 4034791392, 4228891128, 520351806, 132152335, 3237486465,
   4030661600, 2114437372, 264370207, 2213560071, 3766355904, 4228874744,
   528740415, 65043975, 3774615488, 4162814456, 1057222718, 132152847,
   3237744577, 4162814456, 1057222719, 132152839, 3774615488, 4228874744,
   528611391, 66076419, 3766355936, 2114437372, 264305679, 2180521857,
   4162814960, 1057222719, 66092551, 3766355936, 2114445564, 264305679,
   3237744576, 4162814456, 528611359, 2180521857, 4162782192, 1057222719,
   66076419, 4030661616, 1057222719, 66076419, 4030661616, 1057222719,
   66076419, 4030661616, 1057222719, 66076419, 4030661616, 1057222719,
   66076419, 4030661616, 528611359, 2180521857, 4162814456, 532741135,
   3237744576, 4228890750, 132152839, 3766355952, 1057222719, 66076545,
   4162814456, 532741135, 3237744608, 2114445438, 133185283, 4030661112,
   528611343, 3237744576, 4261929086, 133185283, 4028596728, 528546831,
   3237873632, 2114187327, 66592641, 4161782012, 266370567, 4030661616,
   528611343, 3237742560, 2114187327, 66592640, 4228890750, 132136707,
   4028596728, 264306183, 3766420464, 528611343, 3237873632, 1057222687,
   2180779968, 2114449471, 33038272, 4228374655, 66068353, 4228890750,
   133185281, 4162830590, 132136707, 4162814204, 132153091, 4162814204,
   266370819, 4028596476, 266370819, 4162814204, 132153091, 4162830588,
   132136705, 4161782014, 133185409, 4228890750, 66068352, 4228374591,
   33034176, 2114449471, 2180780000, 2130966559, 3237873648, 1065417735,
   3762225656, 264273411, 4028596476, 133185409, 4228898943, 33034176,
   2114187295, 3237873648, 528546823, 3762258428, 266354433, 4161790079,
   66588608, 2114189343, 3229484016, 532741635, 4028612862, 133177216,
   4261933087, 2164131824, 528547335, 4028596478, 133177216, 4261670943,
   3237872624, 532708867, 4162830463, 66588640, 2130835471, 3762225660,
   132136832, 4228378655, 2164130800, 532709123, 4161790079, 33294304,
   1065418247, 4028612734, 66588640, 2130836487, 4030693630, 66068416,
   2130836495, 3762258174, 133177280, 2130836495, 3762258174, 66592704,
   2130836487, 4028596478, 66588640, 1065418247, 4028612735, 33294320,
   532709123, 4161790015, 2164130808, 266354560, 4261672975, 3762258174,
   66588640, 1065418243, 4161790015, 2164130808, 266354560, 4261672975,
   3762258174, 66588640, 1065385729, 4228378655, 3229549052, 133173216,
   1065418243, 4161790015, 3229549052, 133177280, 1065418243, 4161794079,
   3229549052, 66588640, 1065418497, 4228378655, 3762258174, 33294320,
   532692864, 4261673991, 4028620863, 2164130300, 133173216, 1065418497,
   4228380687, 3762274431, 16647160, 133177280, 1065418497, 4228380687,
   3760177279, 2164130812, 133173216, 1069580032, 4261673991, 4027572255,
   3229581566, 33294328, 267395008, 1065418497, 4261672967, 4027572287,
   3229581566, 33293304, 133177312, 1069580160, 4278320131, 4161269775,
   3760177215, 2155806974, 33293304, 133173216, 532692864, 2130771457,
   4228118535, 4027572255, 3225403519, 2164195838, 66847736, 133173216,
   534790080, 2139127552, 4261543427, 4228380679, 4027576351, 3762274367,
   2155839743, 16646654, 66847736, 133697520, 266346464, 1069563776,
   2139127552, 4278320641, 4261673987, 4228380679, 4027576335, 3760185375,
   3762274367, 3229581439, 2155806975, 16646654, 33424380, 66847740,
   133695480, 133697520, 267390960, 266346464, 534781920, 1069563840,
   1069563840, 1069580160, 2139127680, 2139127680, 2139160320, 4278255360,
   4278255360, 4278255360, 4278255360, 4278255360, 4278255360, 4278255360,
   4278255360, 4278255360, 4278255360, 4278255360, 4286611328, 2139127680,
   2139127680, 2143305664, 1069563840, 1069555680, 534781920, 534777840,
   267390960, 133695480, 133694460, 66847742, 33423870, 16711935,
   16744575, 2155855935, 3225411615, 3760189455, 4027578375, 4161010691,
   4227988993, 4278255360, 2139127744, 1069555680, 535826416, 133695484,
   66847230, 33489151, 2155839551, 3223314463, 4027578375, 4161010689,
   4261478144, 2139127744, 1071652848, 267913212, 66978303, 16744575,
   3225411615, 4027578375, 4228120065, 4278255488, 1069555680, 267388924,
   66978303, 8355903, 3223318543, 4161272833, 4261478272, 2143297504,
   267913212, 33423615, 2155855903, 3759142919, 4227989248, 4286595040,
   535824376, 66978047, 8372255, 4027578371, 4261543680, 2143297520,
   267912190, 16711807, 3223318535, 4228120064, 4286595040, 267913212,
   33489023, 3223318535, 4227988992, 4286595040, 267912190, 16744511,
   3759142915, 4261478272, 1071648760, 66978047, 2151669775, 4161011200,
   4286595040, 133956095, 8372255, 4027055104, 4286595040, 267912190,
   8372255, 4027055104, 4286595040, 267911679, 8372239, 4161011200,
   4290781168, 134086911, 2151673863, 4227989376, 1071646716, 33521727,
   3758619649, 4286595040, 133956095, 2151669767, 4227923840, 1072695294,
   16744479, 4026793472, 4290781176, 67043455, 3759143937, 4286595056,
   134086911, 3223320579, 4278222816, 268173823, 2149576707, 4261445568,
   268173823, 2149576707, 4261445600, 268173567, 2149578755, 4278206432,
   134086911, 3222272001, 4286586864, 67043391, 3758620160, 2143293436,
   16760863, 4160880512, 535823359, 4190211, 4261445600, 134086783,
   3758620160, 4290777084, 16760847, 4227923904, 268173567, 3222273024,
   4290776960, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
   };



/********************************* Prototypes **************************/
static void echoCallback(RF_Handle h, RF_CmdHandle ch, RF_EventMask e);


/*************************** Driver handles ****************************/
/* RF driver handle */
static RF_Object rfObject;
static RF_Handle rfHandle;

/* Pin driver handle */
static PIN_Handle ledPinHandle;
static PIN_State ledPinState;

/* GPIO driver handle */
static PIN_Handle gpioPinHandle;
static PIN_State gpioPinState;

/* Timer handle */
GPTimerCC26XX_Handle hTimer1s;
GPTimerCC26XX_Handle hTimer30ms;

/* Buffer which contains all Data Entries for receiving data.
 * Pragmas are needed to make sure this buffer is aligned to a 4 byte boundary
 * (requirement from the RF core)
 */
#if defined(__TI_COMPILER_VERSION__)
#pragma DATA_ALIGN(rxDataEntryBuffer, 4)
static uint8_t
rxDataEntryBuffer[RF_QUEUE_DATA_ENTRY_BUFFER_SIZE(NUM_DATA_ENTRIES,
                                                  MAX_LENGTH,
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
//static uint16_t seqNumber;
static volatile bool bRxSuccess = false;

/* Receive dataQueue for RF Core to fill in data */
static dataQueue_t dataQueue;
static rfc_dataEntryGeneral_t* currentDataEntry;
static uint8_t packetLength;
static uint8_t* packetDataPointer;

static uint8_t txPacket[PAYLOAD_LENGTH] = {(uint8_t)(TRANSMITTER_ID >> 8), (uint8_t)(TRANSMITTER_ID)};

static uint8_t packet[MAX_LENGTH + NUM_APPENDED_BYTES - 1]; /* The length byte is stored in a separate variable */


#ifdef LOG_RADIO_EVENTS
static volatile RF_EventMask eventLog[32];
static volatile uint8_t evIndex = 0;
#endif // LOG_RADIO_EVENTS


/*************************** Configurations ****************************/

/*
 * Application LED pin configuration table:
 *   - All LEDs board LEDs are off.
 */
PIN_Config pinTable[] =
{
#if defined(Board_CC1350_LAUNCHXL)
 Board_DIO30_SWPWR | PIN_GPIO_OUTPUT_EN | PIN_GPIO_HIGH | PIN_PUSHPULL | PIN_DRVSTR_MAX,
#endif
 Board_PIN_LED1 | PIN_GPIO_OUTPUT_EN | PIN_GPIO_LOW | PIN_PUSHPULL | PIN_DRVSTR_MAX,
 Board_PIN_LED2 | PIN_GPIO_OUTPUT_EN | PIN_GPIO_LOW | PIN_PUSHPULL | PIN_DRVSTR_MAX,
 PIN_TERMINATE
};

PIN_Config GPIOpinTable[] =
{
    Board_DIO22 | PIN_GPIO_OUTPUT_EN | PIN_GPIO_LOW | PIN_PUSHPULL | PIN_DRVSTR_MAX,
    PIN_TERMINATE
};

/*************************** Function Defenitions ****************************/


/* 1s timer interrupt */
void timerCallback1s(GPTimerCC26XX_Handle handle, GPTimerCC26XX_IntMask interruptMask) {

    /*Set Pin22 high, to start the audio transmission*/
    PIN_setOutputValue(gpioPinHandle, Board_DIO22, 1);
    PIN_setOutputValue(gpioPinHandle, Board_DIO22, 0);

    rfTransmission = true;

}



void *mainThread(void *arg0)
{
    /*System_Printf over UART */
    Display_Handle display;
    display = Display_open(Display_Type_HOST, NULL);
    UART_init();
    UARTUtils_systemInit(0);


//    System_printf("Setting up \r\n");
//    System_flush();
    uint32_t curtime;
    memcpy(referenceDataChirp, dataChirp, (CHIRPDATASIZE*4));
    RF_Params rfParams;
    RF_Params_init(&rfParams);

    /* Open LED pins */
    ledPinHandle = PIN_open(&ledPinState, pinTable);
    if (ledPinHandle == NULL)
    {
        while(1);
    }

    /* Open GPIO pins */
    gpioPinHandle = PIN_open(&gpioPinState, GPIOpinTable);
    if (gpioPinHandle == NULL)
    {
        while(1);
    }

    /* Call driver init functions */
    GPIO_init();
    PIN_setOutputValue(gpioPinHandle, Board_DIO22, 0);


    if( RFQueue_defineQueue(&dataQueue,
                                rxDataEntryBuffer,
                                sizeof(rxDataEntryBuffer),
                                NUM_DATA_ENTRIES,
                                MAX_LENGTH + NUM_APPENDED_BYTES))
    {
        /* Failed to allocate space for all data entries */
        PIN_setOutputValue(ledPinHandle, Board_PIN_LED1, 1);
        PIN_setOutputValue(ledPinHandle, Board_PIN_LED2, 1);
        while(1);
    }

    /* Modify CMD_PROP_TX and CMD_PROP_RX commands for application needs */
    RF_cmdPropTx.pktLen = PAYLOAD_LENGTH;
    RF_cmdPropTx.pPkt = txPacket;
    RF_cmdPropTx.startTrigger.triggerType = TRIG_ABSTIME;
    RF_cmdPropTx.startTrigger.pastTrig = 1;
    RF_cmdPropTx.startTime = 0;
    RF_cmdPropTx.pNextOp = (rfc_radioOp_t *)&RF_cmdPropRx;
    /* Only run the RX command if TX is successful */
    RF_cmdPropTx.condition.rule = COND_STOP_ON_FALSE;



    /* Modify CMD_PROP_RX command for application needs */
    /* Set the Data Entity queue for received data */
    RF_cmdPropRx.pQueue = &dataQueue;
    /* Discard ignored packets from Rx queue */
    RF_cmdPropRx.rxConf.bAutoFlushIgnored = 1;
    /* Discard packets with CRC error from Rx queue */
    RF_cmdPropRx.rxConf.bAutoFlushCrcErr = 1;
    /* Implement packet length filtering to avoid PROP_ERROR_RXBUF */
    RF_cmdPropRx.maxPktLen = MAX_LENGTH;
    RF_cmdPropRx.pktConf.bRepeatOk = 0;
    RF_cmdPropRx.pktConf.bRepeatNok = 0;
    RF_cmdPropRx.pOutput = (uint8_t *)&rxStatistics;
    /* Receive operation will end RX_TIMEOUT ms after command starts */
    RF_cmdPropRx.endTrigger.triggerType = TRIG_REL_PREVEND;
    RF_cmdPropRx.endTime = RX_TIMEOUT;



    /* Request access to the radio */
#if defined(DeviceFamily_CC26X0R2)
    rfHandle = RF_open(&rfObject, &RF_prop, (RF_RadioSetup*)&RF_cmdPropRadioSetup, &rfParams);
#else
    rfHandle = RF_open(&rfObject, &RF_prop, (RF_RadioSetup*)&RF_cmdPropRadioDivSetup, &rfParams);
#endif// DeviceFamily_CC26X0R2

    /* Set the frequency */
    RF_postCmd(rfHandle, (RF_Op*)&RF_cmdFs, RF_PriorityNormal, NULL, 0);

    /*Timer interrupt settings: generate interrupt every second*/

     GPTimerCC26XX_Params timerParams1s;
     GPTimerCC26XX_Params_init(&timerParams1s);
     timerParams1s.width          = GPT_CONFIG_32BIT;
     timerParams1s.mode           = GPT_MODE_PERIODIC_UP;
     timerParams1s.debugStallMode = GPTimerCC26XX_DEBUG_STALL_OFF;
     hTimer1s = GPTimerCC26XX_open(CC1310_LAUNCHXL_GPTIMER0A, &timerParams1s);
     if(hTimer1s == NULL) {
      while(1);
     }

     xdc_runtime_Types_FreqHz freq;
     BIOS_getCpuFreq(&freq);
     GPTimerCC26XX_Value loadVal1s = (freq.lo) - 1; // setting timer to load value equal to 1s
     GPTimerCC26XX_setLoadValue(hTimer1s, loadVal1s);
     GPTimerCC26XX_registerInterrupt(hTimer1s, timerCallback1s, GPT_INT_TIMEOUT);


     /*Start the tilmer*/
     GPTimerCC26XX_start(hTimer1s);

    while(1)
    {
        /* STEP 1: TRANSMITTING WAKE UP SIGNAL */

        /* Transmit a packet and wait for its echo.
        * - When the first of the two chained commands (TX) completes, the
        * RF_EventCmdDone event is raised but not RF_EventLastCmdDone

        */
        /* STEP 2: WAIT FOR RECEIVER SIGNAL
        * - The RF_EventLastCmdDone in addition to the RF_EventCmdDone events
        * are raised when the second, and therefore last, command (RX) in the
        * chain completes
        * -- If the RF core successfully receives the echo it will also raise
        * the RF_EventRxEntryDone event
        * -- If the RF core times out while waiting for the echo it does not
        * raise the RF_EventRxEntryDone event
        */

        if(rfTransmission){

        PIN_setOutputValue(gpioPinHandle, Board_DIO22, 0);

        curtime = RF_getCurrentTime();
        curtime += PACKET_INTERVAL;
        RF_cmdPropTx.startTime = curtime;

//        PIN_setOutputValue(gpioPinHandle, Board_DIO22, 1);
//        PIN_setOutputValue(gpioPinHandle, Board_DIO22, 0);

        rfTransmission = false;

        RF_EventMask terminationReason =
        RF_runCmd(rfHandle, (RF_Op*)&RF_cmdPropTx, RF_PriorityNormal,
                  echoCallback, (RF_EventCmdDone | RF_EventRxEntryDone |
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

        uint32_t cmdStatus = ((volatile RF_Op*)&RF_cmdPropTx)->status;
        switch(cmdStatus)
        {
            case PROP_DONE_OK:
                // Packet transmitted successfully
                break;
            case PROP_DONE_STOPPED:
                // received CMD_STOP while transmitting packet and finished
                // transmitting packet
                break;
            case PROP_DONE_ABORT:
                // Received CMD_ABORT while transmitting packet
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
            case PROP_ERROR_TXUNF:
                // TX underflow observed during operation
                break;
            default:
                // Uncaught error event - these could come from the
                // pool of states defined in rf_mailbox.h
                while(1);
            }

        System_printf("Distance \r\n");
        System_printf("%lf\r\n" , distance);
//        System_flush();
        }

    }
}

static int pop(unsigned x)
{
    unsigned long long y;
    y = x * 0x0002000400080010ULL;
    y = y & 0x1111111111111111ULL;
    y = y * 0x1111111111111111ULL;
    y = y >> 60;
    return y;

}

static void echoCallback(RF_Handle h, RF_CmdHandle ch, RF_EventMask e)
{
#ifdef LOG_RADIO_EVENTS
    eventLog[evIndex++ & 0x1F] = e;
#endif// LOG_RADIO_EVENTS

    memcpy(referenceDataChirp, dataChirp, (CHIRPDATASIZE*4));

    if((e & RF_EventCmdDone) && !(e & RF_EventLastCmdDone))
    {
        /* Successful TX */
        /* Toggle LED1, clear LED2 to indicate TX */
        PIN_setOutputValue(ledPinHandle, Board_PIN_LED1,
                           !PIN_getOutputValue(Board_PIN_LED1));
        PIN_setOutputValue(ledPinHandle, Board_PIN_LED2, 0);
    }
    else if(e & RF_EventRxEntryDone)
    {

        /*For testing the round trip time of RF tx and Rx*/
//        PIN_setOutputValue(gpioPinHandle, Board_DIO22, 1);
//        PIN_setOutputValue(gpioPinHandle, Board_DIO22, 0);
//        PIN_setOutputValue(gpioPinHandle, Board_DIO22, 1);
//        PIN_setOutputValue(gpioPinHandle, Board_DIO22, 0);
//        PIN_setOutputValue(gpioPinHandle, Board_DIO22, 1);
//        PIN_setOutputValue(gpioPinHandle, Board_DIO22, 0);

        unsigned int u = SAMPLEBITSIZE-1;         // Goes upto SAMPLEDATASIZE (32)
        unsigned int v = 0;        // Goes to CHIRPDATASIZE (469)
        unsigned int w = 0;      // Goes to SAMPLEDATASIZE (16)
        //unsigned short result[((CHIRPDATAPAIRS-1)*(SAMPLEBITSIZE-1))+1];
        unsigned int result = 0;
        unsigned int tempResult = 0;
        unsigned int index = 0;

        /* Toggle pin to indicate RX */
        PIN_setOutputValue(ledPinHandle, Board_PIN_LED2,
                           !PIN_getOutputValue(Board_PIN_LED2));

        /* Get current unhandled data entry */
        currentDataEntry = RFQueue_getDataEntry();

        /* Handle the packet data, located at &currentDataEntry->data:
         * - Length is the first byte with the current configuration
         * - Data starts from the second byte */
        packetLength      = *(uint8_t*)(&currentDataEntry->data);
        packetDataPointer = (uint8_t*)(&currentDataEntry->data + 1);

        /* Copy the payload + the status byte to the packet variable */
        memcpy(packet, packetDataPointer, (packetLength + 1));

        uint_fast16_t i = 0;
        uint_fast16_t j = 0;
        for(i = 2; i < packetLength; i=i+4)
        {   j = (i-2)/4;
            packetADC[j]= ((unsigned long)packetDataPointer[i] << 24) | ((unsigned long)packetDataPointer[i+1] << 16) | ((unsigned long)packetDataPointer[i+2] << 8) | packetDataPointer[(i+3)];
        }


        for(u=0; u<SAMPLEBITSIZE; u++){

                for(v=0; v<(CHIRPDATAPAIRS); v++){

                                    tempResult = 0;
                                    //Hamming weight calculations
                                    for(w= 0; w<SAMPLEDATASIZE; w++){
                                        tempResult += pop(~(referenceDataChirp[(v*SAMPLEDATASIZE+w)] ^ packetADC[w]));

                                        //bitshift
                                        referenceDataChirp[(v*SAMPLEDATASIZE+w)] <<= 1;
                                        if((referenceDataChirp[(v*SAMPLEDATASIZE+w)+1] & mask) == mask){
                                            referenceDataChirp[(v*SAMPLEDATASIZE+w)] += 1;
                                        }



                                    }
                                    if(tempResult >= result){
                                                            index = ((u) +(v*SAMPLEBITSIZE));
                                                            result = tempResult;

                                                        }
                              }

            }


//        distance = (14488-index)*0.000686;
//        System_printf("Result: %u\n" , result);
//        System_printf("Index: %u\n" , index);
//      System_printf("Distance:\r\n");
//      System_flush();
//      System_printf("%lf\r\n" , distance);
//        System_printf("Distance%lf \r\n", distance);
//        System_printf(distance);



        RFQueue_nextEntry();
    }
    else if((e & RF_EventLastCmdDone) && !(e & RF_EventRxEntryDone))
        {
            if(bRxSuccess == true)
            {
                /* Received packet successfully but RX command didn't complete at
                 * the same time RX_ENTRY_DONE event was raised. Reset the flag
                 */
                bRxSuccess = false;
            }
            else
            {
                /* RX timed out */
                /* Set LED2, clear LED1 to indicate TX */
                PIN_setOutputValue(ledPinHandle, Board_PIN_LED1, 0);
                PIN_setOutputValue(ledPinHandle, Board_PIN_LED2, 1);
            }
        }
        else
        {
            /* Error Condition: set both LEDs */
            PIN_setOutputValue(ledPinHandle, Board_PIN_LED1, 1);
            PIN_setOutputValue(ledPinHandle, Board_PIN_LED2, 1);
        }
    }
