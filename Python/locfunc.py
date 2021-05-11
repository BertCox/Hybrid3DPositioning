import numpy as np
from numpy.linalg import inv
import scipy as sp
from scipy.optimize import minimize
import sympy as sy
import matplotlib.pyplot as plt
from matplotlib import rc


def estimate_xy(X_Tx, Y_Tx, DeltasSquared):
    # X_Tx, Y_Tx, DeltaSquared are a row array, shape 1,N
    # DeltaSquared is the square of the planar distances!

    b = np.zeros((X_Tx.shape[1] - 1, 1))
    M = np.zeros((X_Tx.shape[1] - 1, 2))

    Fixed = DeltasSquared[X_Tx.shape[1] - 1] - X_Tx[0, X_Tx.shape[1] - 1] ** 2 - Y_Tx[0, Y_Tx.shape[1] - 1] ** 2

    M[:, 0] = X_Tx[0, 0:X_Tx.shape[1] - 1] - X_Tx[0, X_Tx.shape[1] - 1]
    M[:, 1] = Y_Tx[0, 0:Y_Tx.shape[1] - 1] - Y_Tx[0, Y_Tx.shape[1] - 1]

    M = (-2) * M
    b[:, 0] = DeltasSquared[0:X_Tx.shape[1] - 1] - X_Tx[0, 0:X_Tx.shape[1] - 1] ** 2 - Y_Tx[0, 0:Y_Tx.shape[
                                                                                                     1] - 1] ** 2 - Fixed
    Est = np.dot(np.dot(inv(np.dot(np.transpose(M), M)), np.transpose(M)), b)

    return Est


def calc_distance_3D(x, y, z, xc, yc, zc):
    """
    OK
    :param x: mesh
    :param y: mesh
    :param z: mesh
    :param xc: beacon x
    :param yc: beacon y
    :param zc: beacon z
    :return:
    """
    return np.sqrt((x - xc) ** 2 + (y - yc) ** 2 + (z - zc) ** 2)


def estimate_xyz(X_Tx, Y_Tx, Z_Tx, d_meas):
    """

    :param X_Tx: beacons x_coords
    :param Y_Tx: beacons y_coords
    :param Z_Tx:  beacons z_coords
    :param d_meas:
    :return:
    """
    # determine rows of A
    norm_tool = np.array([X_Tx[0], Y_Tx[0], Z_Tx[0]])
    norm_r = d_meas[0] ** 2
    d_measn = d_meas[1:]
    X_Txn = X_Tx[1:]
    Y_Txn = Y_Tx[1:]
    Z_Txn = Z_Tx[1:]

    a0 = (X_Txn - norm_tool[0])
    a1 = (Y_Txn - norm_tool[1])
    a2 = (Z_Txn - norm_tool[2])
    A = np.stack((a0, a1, a2))
    A = A.transpose()

    B = 0.5 * (norm_r - d_measn ** 2 + calc_distance_3D(X_Txn, Y_Txn, Z_Txn, norm_tool[0], norm_tool[1],
                                                        norm_tool[2]) ** 2)
    B = B[:, np.newaxis]
    Est = np.dot(np.dot(np.linalg.pinv(np.dot(np.transpose(A), A)), np.transpose(A)), B)
    return Est.ravel() + norm_tool.ravel()


def mse3D(x, locations, distances):
    """
    Better result in optimization when including Z coordinate as a variable (ignore Z result though)
    Mean squared error calculation
    """
    mse = 0.0
    teller = 0

    for location, distance in zip(locations, distances):
        distance_calculated = np.sqrt((x[0] - location[0]) ** 2 + (x[1] - location[1]) ** 2 + (x[2] - location[2]) ** 2)
        mse += (distance_calculated - distance) ** 2
        teller += 1

    return mse / float(teller)


def estimate_xyz_NLSE(XT, YT, ZT, d_s_masked, prev_posit):
    """

    :param locations: beacon locations
    :param d_s_masked: 3D euclidean distance
    :param prev_posit: initial guess for optimization
    :return: location in result.x
    """
    locations = []
    for xl, yl, zl in zip(XT, YT, ZT):
        locations.append(np.array([xl, yl, zl]))
    result = minimize(
        mse3D,  # The error function
        np.array(prev_posit),  # The initial guess
        args=(locations, d_s_masked),  # Additional parameters for mse
        method='L-BFGS-B',  # The optimisation algorithm
        # bounds=[(-1, 4), (0, 40), (0., 15)],
        options={
            'ftol': 1e-17,  # Tolerance
            'maxiter': 1e+7,
            'disp': False,
        })

    return result


def estimate_xyz_NLSE_location(XT, YT, ZT, d_s_masked, prev_posit):
    """

    :param locations: beacon locations
    :param d_s_masked: 3D euclidean distance
    :param prev_posit: initial guess for optimization
    :return: location in result.x
    """
    locations = []
    for xl, yl, zl in zip(XT, YT, ZT):
        locations.append(np.array([xl, yl, zl]))
    result = minimize(
        mse3D,  # The error function
        np.array(prev_posit),  # The initial guess
        args=(locations, d_s_masked),  # Additional parameters for mse
        method='L-BFGS-B',  # The optimisation algorithm
        # bounds=[(-1, 4), (0, 40), (0., 15)],
        options={
            'ftol': 1e-17,  # Tolerance
            'maxiter': 1e+7,
            'disp': False,
        })

    return result


def mse(x, locations, distances):
    """
    Better result in optimization when including Z coordinate as a variable (ignore Z result though)???
    Mean squared error calculation
    distances are planar distances
    """
    mse = 0.0
    teller = 0
    for location, distance in zip(locations, distances):
        distance_calculated = np.sqrt((x[0] - location[0]) ** 2 + (x[1] - location[1]) ** 2)
        mse += (distance_calculated - distance) ** 2
        teller += 1

    return mse / float(teller)


def estimate_xy_NLSE(XT, YT, d_s_masked, prev_posit):
    """

    :param locations: beacon locations
    :param d_s_masked: 3D euclidean distance
    :param prev_posit: initial guess for optimization
    :return: location in result.x
    """
    locations = []
    for xl, yl in zip(XT, YT):
        locations.append(np.array([xl, yl]))
    result = minimize(
        mse,  # The error function
        np.array(prev_posit),  # The initial guess
        args=(locations, d_s_masked),  # Additional parameters for mse
        method='L-BFGS-B',  # The optimisation algorithm
        # bounds=[(-1, 4), (0, 40), (0., 15)],
        options={
            'ftol': 1e-10,  # Tolerance
            'maxiter': 1e+7,
            'disp': False,
        })

    return result


def estimate_xyz_SimpleIntersection(S, N, r):
    """
    :param S: Matrix of the speaker positions
    :param N: amount of speakers
    :param distances to the speaker
    :return: location x
    """
    A = 2 * S
    b = np.sum(np.power(S, 2), axis=1) - np.power(r, 2)
    b = b[:, np.newaxis]
    D = np.hstack((-np.ones((N - 1, 1)), np.eye(N - 1)))
    result = inv(A.T @ D.T @ D @ A) @ A.T @ D.T @ D @ b
    return result.flatten()


def estimate_xyz_RangeBancroft(S, N, r):
    A = 2 * S
    b = np.sum(np.power(S, 2), axis=1) - np.power(r, 2)
    b = b[:, np.newaxis]
    ones = np.ones((N, 1))
    p = inv(A.T @ A) @ A.T @ ones
    q = inv(A.T @ A) @ A.T @ b
    x, y, z = p.T @ p, 2 * p.T @ q - 1, q.T @ q
    v = np.concatenate((x[0], y[0], z[0]))
    t = np.roots(v)
    result1 = p @ [t[0]] + q.flatten()
    result1b = result1[:, np.newaxis]
    result2 = p @ [t[1]] + q.flatten()
    result2b = result2[:, np.newaxis]

    norm1 = np.linalg.norm(r - np.sqrt(np.sum(np.power(S - ones @ result1b.T, 2), axis=1)))
    norm2 = np.linalg.norm(r - np.sqrt(np.sum(np.power(S - ones @ result2b.T, 2), axis=1)))
    if norm1 < norm2:
        result = result1
    else:
        result = result2
    return np.absolute(result).flatten()


def estimate_xyz_Beck(S, N, r):
    A = np.hstack((2 * S, -np.ones((N, 1))))
    b = np.sum(np.power(S, 2), axis=1) - np.power(r, 2)
    b = b[:, np.newaxis]
    P = np.diag([1, 1, 1, 0])
    q = np.array((0, 0, 0, -0.5))[:, np.newaxis]
    lambda_1 = np.max(np.linalg.eigvals(sp.linalg.sqrtm((A.T @ A)) @ P @ sp.linalg.sqrtm((A.T @ A))))
    tolerance = 1 * 10 ** (-10)

    def functionPhi(x):
        z = inv(A.T @ A + x * P) @ (A.T @ b - x * q)
        phi = (z.T @ P @ z + 2 * q.T @ z).flatten()[0]
        return phi

    # TODO check right boundry, currently set at 1000, doens't work when put on np.INF
    try:
        t = sp.optimize.bisect(f=functionPhi, a=-1 / lambda_1, b=1000, xtol=tolerance)
    except:
        return np.array((0,0,0))
    theta = inv(A.T @ A + t * P) @ (A.T @ b - t * q)
    return np.absolute(theta[0:3]).flatten()


def estimate_xyz_Chueng(S, N, r):
    eye = np.eye(N)
    A = np.hstack((S, -0.5 * np.ones((N, 1))))
    b = 0.5 * np.sum(np.power(S, 2), axis=1) - 0.5 * np.power(r, 2)
    b = b[:, np.newaxis]
    r_matrix = np.reshape(2*r, (N, 1))
    Psi = r_matrix @ r_matrix.T * eye
    invPsi = inv(Psi)
    P = np.diag([1, 1, 1, 0])
    q = np.array((0, 0, 0, -1))[:, np.newaxis]

    [L, U] = np.linalg.eig((inv(A.T @ invPsi @ A) @ P))
    z = np.sort(L)[::-1]
    si = np.argsort(L)[::-1]
    U2 = U[:, si]
    c = (U2.T @ q).flatten()
    g = (inv(U2) @ inv((A.T @ invPsi @ A)) @ q).flatten()
    e = ((invPsi @ A @ U2).T @ b).flatten()
    f = (inv(U2) @ inv((A.T @ invPsi @ A)) @ A @ invPsi @ b).flatten()

    # solve the five root equation
    lam = sy.symbols('lam')
    expr = c[3] * f[3] \
           - (lam / 2) * c[3] * g[3] \
           + ((c[2] * f[2]) / (1 + lam * z[2])) + ((c[1] * f[1]) / (1 + lam * z[1])) + (
                       (c[0] * f[0]) / (1 + lam * z[0])) \
           - (lam / 2) * (((c[2] * g[2]) / (1 + lam * z[2])) + ((c[1] * g[1]) / (1 + lam * z[1])) + (
                (c[0] * g[0]) / (1 + lam * z[0]))) \
           + ((e[2] * f[2] * z[2]) / ((1 + lam * z[2]) ** 2)) + ((e[1] * f[1] * z[1]) / ((1 + lam * z[1]) ** 2)) + (
                       (e[0] * f[0] * z[0]) / ((1 + lam * z[0]) ** 2)) \
           - (lam / 2) * ((((e[2] * g[2] + c[2] * f[2]) * z[2]) / (1 + lam * z[2]) ** 2) + (
                ((e[1] * g[1] + c[1] * f[1]) * z[1]) / (1 + lam * z[1]) ** 2) + (
                                      ((e[0] * g[0] + c[0] * f[0]) * z[0]) / (1 + lam * z[0]) ** 2)) \
           + ((lam ** 2) / 4) * (((c[2] * g[2] * z[2]) / (1 + lam * z[2]) ** 2) + (
                (c[1] * g[1] * z[1]) / (1 + lam * z[1]) ** 2) + ((c[0] * g[0] * z[0]) / (1 + lam * z[0]) ** 2))

    lambda_star = np.array(list(sy.solveset(expr, lam,  domain= sy.Reals)), dtype=np.float_)
    fval = np.zeros(len(lambda_star))
    theta = np.zeros((4, len(lambda_star)))
    for i in range(len(lambda_star)):
       try:
           theta[:,i] = (inv((A.T @ invPsi @ A + lambda_star[i] * P)) @ (A.T @ invPsi @ b - (lambda_star[i]/2) * q)).flatten()
           fval[i] = ((A @ theta[:,i])[:, np.newaxis] - b).T @ invPsi @ ((A @ theta[:,i])[:, np.newaxis] - b)
       except:
           fval[i] = np.infty
    minIndex = np.argmin(fval)

    # result = theta[0:3, minIndex].flatten()
    # lambda_star_selected = lambda_star[lambda_star > 0]
    # idx = (np.abs(lambda_star - 0)).argmin()
    # lambda_star_final = lambda_star[idx]

    # try:
    #     lambda_star_final = lambda_star_selected[0]
    # except:
    #     result = np.zeros(3)
    #     return result
    # try:
    #     result = inv((A.T @ invPsi @ A + lambda_star_final * P)) @ (A.T @ invPsi @ b - (lambda_star_final/2) * q)
    # except:
    #     result = np.linalg.pinv((A.T @ invPsi @ A + lambda_star_final * P)) @ (A.T @ invPsi @ b - (lambda_star_final/2) * q)
    # print(result[0:3].flatten())
    return theta[0:3, minIndex].flatten()

def estimate_xyz_Chueng2(S, N, r):
    eye = np.eye(N)
    A = np.hstack((S, -0.5 * np.ones((N, 1))))
    b = 0.5 * np.sum(np.power(S, 2), axis=1) - 0.5 * np.power(r, 2)
    b = b[:, np.newaxis]
    r_matrix = np.reshape(2*r, (N, 1))
    Psi = r_matrix @ r_matrix.T * eye
    invPsi = inv(Psi)
    P = np.diag([1, 1, 1, 0])
    q = np.array((0, 0, 0, -1))[:, np.newaxis]

    [L, U] = np.linalg.eig((inv(A.T @ invPsi @ A) @ P))
    z = np.sort(L)[::-1]
    si = np.argsort(L)[::-1]
    U2 = U[:, si]
    c = (U2.T @ q).flatten()
    g = (inv(U2) @ inv((A.T @ invPsi @ A)) @ q).flatten()
    e = ((invPsi @ A @ U2).T @ b).flatten()
    f = (inv(U2) @ inv((A.T @ invPsi @ A)) @ A @ invPsi @ b).flatten()

    # solve the five root equation
    # lam = sy.symbols('lam')
    p =  np.zeros(8)
    p[7] = c[0] * f[0] + c[1] * f[1] + c[2] * f[2] + c[3] * f[3] + e[0] * f[0] * z[0] + e[1] * f[1] * z[1] + e[2] * f[2] * z[2]
    p[6] = c[0]*f[0]*z[0]/2 + 2*c[0]*f[0]*z[1] + 2*c[0]*f[0]*z[2] - c[0]*g[0]/2 + 2*c[1]*f[1]*z[0] + c[1]*f[1]*z[1]/2 + 2*c[1]*f[1]*z[2] - c[1]*g[1]/2 + 2*c[2]*f[2]*z[0] + 2*c[2]*f[2]*z[1] + c[2]*f[2]*z[2]/2 - c[2]*g[2]/2 + 2*c[3]*f[3]*z[0] + 2*c[3]*f[3]*z[1] + 2*c[3]*f[3]*z[2] + c[3]*g[3]/2 + 2*e[0]*f[0]*z[0]*z[1] + 2*e[0]*f[0]*z[0]*z[2] - e[0]*g[0]*z[0]/2 + 2*e[1]*f[1]*z[0]*z[1] + 2*e[1]*f[1]*z[1]*z[2] - e[1]*g[1]*z[1]/2 + 2*e[2]*f[2]*z[0]*z[2] + 2*e[2]*f[2]*z[1]*z[2] - e[2]*g[2]*z[2]/2
    p[5] = c[0]*f[0]*z[0]*z[1] + c[0]*f[0]*z[0]*z[2] + c[0]*f[0]*z[1]**2 + 4*c[0]*f[0]*z[1]*z[2] + c[0]*f[0]*z[2]**2 - c[0]*g[0]*z[0]/4 - c[0]*g[0]*z[1] - c[0]*g[0]*z[2] + c[1]*f[1]*z[0]**2 + c[1]*f[1]*z[0]*z[1] + 4*c[1]*f[1]*z[0]*z[2] + c[1]*f[1]*z[1]*z[2] + c[1]*f[1]*z[2]**2 - c[1]*g[1]*z[0] - c[1]*g[1]*z[1]/4 - c[1]*g[1]*z[2] + c[2]*f[2]*z[0]**2 + 4*c[2]*f[2]*z[0]*z[1] + c[2]*f[2]*z[0]*z[2] + c[2]*f[2]*z[1]**2 + c[2]*f[2]*z[1]*z[2] - c[2]*g[2]*z[0] - c[2]*g[2]*z[1] - c[2]*g[2]*z[2]/4 + c[3]*f[3]*z[0]**2 + 4*c[3]*f[3]*z[0]*z[1] + 4*c[3]*f[3]*z[0]*z[2] + c[3]*f[3]*z[1]**2 + 4*c[3]*f[3]*z[1]*z[2] + c[3]*f[3]*z[2]**2 + c[3]*g[3]*z[0] + c[3]*g[3]*z[1] + c[3]*g[3]*z[2] + e[0]*f[0]*z[0]*z[1]**2 + 4*e[0]*f[0]*z[0]*z[1]*z[2] + e[0]*f[0]*z[0]*z[2]**2 - e[0]*g[0]*z[0]*z[1] - e[0]*g[0]*z[0]*z[2] + e[1]*f[1]*z[0]**2*z[1] + 4*e[1]*f[1]*z[0]*z[1]*z[2] + e[1]*f[1]*z[1]*z[2]**2 - e[1]*g[1]*z[0]*z[1] - e[1]*g[1]*z[1]*z[2] + e[2]*f[2]*z[0]**2*z[2] + 4*e[2]*f[2]*z[0]*z[1]*z[2] + e[2]*f[2]*z[1]**2*z[2] - e[2]*g[2]*z[0]*z[2] - e[2]*g[2]*z[1]*z[2]
    p[4] = c[0]*f[0]*z[0]*z[1]**2/2 + 2*c[0]*f[0]*z[0]*z[1]*z[2] + c[0]*f[0]*z[0]*z[2]**2/2 + 2*c[0]*f[0]*z[1]**2*z[2] + 2*c[0]*f[0]*z[1]*z[2]**2 - c[0]*g[0]*z[0]*z[1]/2 - c[0]*g[0]*z[0]*z[2]/2 - c[0]*g[0]*z[1]**2/2 - 2*c[0]*g[0]*z[1]*z[2] - c[0]*g[0]*z[2]**2/2 + c[1]*f[1]*z[0]**2*z[1]/2 + 2*c[1]*f[1]*z[0]**2*z[2] + 2*c[1]*f[1]*z[0]*z[1]*z[2] + 2*c[1]*f[1]*z[0]*z[2]**2 + c[1]*f[1]*z[1]*z[2]**2/2 - c[1]*g[1]*z[0]**2/2 - c[1]*g[1]*z[0]*z[1]/2 - 2*c[1]*g[1]*z[0]*z[2] - c[1]*g[1]*z[1]*z[2]/2 - c[1]*g[1]*z[2]**2/2 + 2*c[2]*f[2]*z[0]**2*z[1] + c[2]*f[2]*z[0]**2*z[2]/2 + 2*c[2]*f[2]*z[0]*z[1]**2 + 2*c[2]*f[2]*z[0]*z[1]*z[2] + c[2]*f[2]*z[1]**2*z[2]/2 - c[2]*g[2]*z[0]**2/2 - 2*c[2]*g[2]*z[0]*z[1] - c[2]*g[2]*z[0]*z[2]/2 - c[2]*g[2]*z[1]**2/2 - c[2]*g[2]*z[1]*z[2]/2 + 2*c[3]*f[3]*z[0]**2*z[1] + 2*c[3]*f[3]*z[0]**2*z[2] + 2*c[3]*f[3]*z[0]*z[1]**2 + 8*c[3]*f[3]*z[0]*z[1]*z[2] + 2*c[3]*f[3]*z[0]*z[2]**2 + 2*c[3]*f[3]*z[1]**2*z[2] + 2*c[3]*f[3]*z[1]*z[2]**2 + c[3]*g[3]*z[0]**2/2 + 2*c[3]*g[3]*z[0]*z[1] + 2*c[3]*g[3]*z[0]*z[2] + c[3]*g[3]*z[1]**2/2 + 2*c[3]*g[3]*z[1]*z[2] + c[3]*g[3]*z[2]**2/2 + 2*e[0]*f[0]*z[0]*z[1]**2*z[2] + 2*e[0]*f[0]*z[0]*z[1]*z[2]**2 - e[0]*g[0]*z[0]*z[1]**2/2 - 2*e[0]*g[0]*z[0]*z[1]*z[2] - e[0]*g[0]*z[0]*z[2]**2/2 + 2*e[1]*f[1]*z[0]**2*z[1]*z[2] + 2*e[1]*f[1]*z[0]*z[1]*z[2]**2 - e[1]*g[1]*z[0]**2*z[1]/2 - 2*e[1]*g[1]*z[0]*z[1]*z[2] - e[1]*g[1]*z[1]*z[2]**2/2 + 2*e[2]*f[2]*z[0]**2*z[1]*z[2] + 2*e[2]*f[2]*z[0]*z[1]**2*z[2] - e[2]*g[2]*z[0]**2*z[2]/2 - 2*e[2]*g[2]*z[0]*z[1]*z[2] - e[2]*g[2]*z[1]**2*z[2]/2
    p[3] = c[0]*f[0]*z[0]*z[1]**2*z[2] + c[0]*f[0]*z[0]*z[1]*z[2]**2 + c[0]*f[0]*z[1]**2*z[2]**2 - c[0]*g[0]*z[0]*z[1]**2/4 - c[0]*g[0]*z[0]*z[1]*z[2] - c[0]*g[0]*z[0]*z[2]**2/4 - c[0]*g[0]*z[1]**2*z[2] - c[0]*g[0]*z[1]*z[2]**2 + c[1]*f[1]*z[0]**2*z[1]*z[2] + c[1]*f[1]*z[0]**2*z[2]**2 + c[1]*f[1]*z[0]*z[1]*z[2]**2 - c[1]*g[1]*z[0]**2*z[1]/4 - c[1]*g[1]*z[0]**2*z[2] - c[1]*g[1]*z[0]*z[1]*z[2] - c[1]*g[1]*z[0]*z[2]**2 - c[1]*g[1]*z[1]*z[2]**2/4 + c[2]*f[2]*z[0]**2*z[1]**2 + c[2]*f[2]*z[0]**2*z[1]*z[2] + c[2]*f[2]*z[0]*z[1]**2*z[2] - c[2]*g[2]*z[0]**2*z[1] - c[2]*g[2]*z[0]**2*z[2]/4 - c[2]*g[2]*z[0]*z[1]**2 - c[2]*g[2]*z[0]*z[1]*z[2] - c[2]*g[2]*z[1]**2*z[2]/4 + c[3]*f[3]*z[0]**2*z[1]**2 + 4*c[3]*f[3]*z[0]**2*z[1]*z[2] + c[3]*f[3]*z[0]**2*z[2]**2 + 4*c[3]*f[3]*z[0]*z[1]**2*z[2] + 4*c[3]*f[3]*z[0]*z[1]*z[2]**2 + c[3]*f[3]*z[1]**2*z[2]**2 + c[3]*g[3]*z[0]**2*z[1] + c[3]*g[3]*z[0]**2*z[2] + c[3]*g[3]*z[0]*z[1]**2 + 4*c[3]*g[3]*z[0]*z[1]*z[2] + c[3]*g[3]*z[0]*z[2]**2 + c[3]*g[3]*z[1]**2*z[2] + c[3]*g[3]*z[1]*z[2]**2 + e[0]*f[0]*z[0]*z[1]**2*z[2]**2 - e[0]*g[0]*z[0]*z[1]**2*z[2] - e[0]*g[0]*z[0]*z[1]*z[2]**2 + e[1]*f[1]*z[0]**2*z[1]*z[2]**2 - e[1]*g[1]*z[0]**2*z[1]*z[2] - e[1]*g[1]*z[0]*z[1]*z[2]**2 + e[2]*f[2]*z[0]**2*z[1]**2*z[2] - e[2]*g[2]*z[0]**2*z[1]*z[2] - e[2]*g[2]*z[0]*z[1]**2*z[2]
    p[2] = c[0]*f[0]*z[0]*z[1]**2*z[2]**2/2 - c[0]*g[0]*z[0]*z[1]**2*z[2]/2 - c[0]*g[0]*z[0]*z[1]*z[2]**2/2 - c[0]*g[0]*z[1]**2*z[2]**2/2 + c[1]*f[1]*z[0]**2*z[1]*z[2]**2/2 - c[1]*g[1]*z[0]**2*z[1]*z[2]/2 - c[1]*g[1]*z[0]**2*z[2]**2/2 - c[1]*g[1]*z[0]*z[1]*z[2]**2/2 + c[2]*f[2]*z[0]**2*z[1]**2*z[2]/2 - c[2]*g[2]*z[0]**2*z[1]**2/2 - c[2]*g[2]*z[0]**2*z[1]*z[2]/2 - c[2]*g[2]*z[0]*z[1]**2*z[2]/2 + 2*c[3]*f[3]*z[0]**2*z[1]**2*z[2] + 2*c[3]*f[3]*z[0]**2*z[1]*z[2]**2 + 2*c[3]*f[3]*z[0]*z[1]**2*z[2]**2 + c[3]*g[3]*z[0]**2*z[1]**2/2 + 2*c[3]*g[3]*z[0]**2*z[1]*z[2] + c[3]*g[3]*z[0]**2*z[2]**2/2 + 2*c[3]*g[3]*z[0]*z[1]**2*z[2] + 2*c[3]*g[3]*z[0]*z[1]*z[2]**2 + c[3]*g[3]*z[1]**2*z[2]**2/2 - e[0]*g[0]*z[0]*z[1]**2*z[2]**2/2 - e[1]*g[1]*z[0]**2*z[1]*z[2]**2/2 - e[2]*g[2]*z[0]**2*z[1]**2*z[2]/2
    p[1] = -c[0]*g[0]*z[0]*z[1]**2*z[2]**2/4 - c[1]*g[1]*z[0]**2*z[1]*z[2]**2/4 - c[2]*g[2]*z[0]**2*z[1]**2*z[2]/4 + c[3]*f[3]*z[0]**2*z[1]**2*z[2]**2 + c[3]*g[3]*z[0]**2*z[1]**2*z[2] + c[3]*g[3]*z[0]**2*z[1]*z[2]**2 + c[3]*g[3]*z[0]*z[1]**2*z[2]**2
    p[0] = c[3]*g[3]*z[0]**2*z[1]**2*z[2]**2/2
    roots = np.roots(p)
    # lambda_star = roots.real
    lambda_star = abs(roots)
    # fval = np.zeros(len(lambda_star))
    # theta = np.zeros((4, len(lambda_star)))
    # for i in range(len(lambda_star)):
    #    try:
    #        theta[:,i] = (inv((A.T @ invPsi @ A + lambda_star[i] * P)) @ (A.T @ invPsi @ b - (lambda_star[i]/2) * q)).flatten()
    #        fval[i] = ((A @ theta[:,i])[:, np.newaxis] - b).T @ invPsi @ ((A @ theta[:,i])[:, np.newaxis] - b)
    #    except:
    #        fval[i] = np.infty
    # minIndex = np.argmin(fval)

    # result = theta[0:3, minIndex].flatten()

    # lambda_star_selected = lambda_star[lambda_star > 0]
    # idx = (np.abs(lambda_star - 0)).argmin()
    # lambda_star_final = lambda_star[idx]
    lambda_star_selected = lambda_star[lambda_star > 0]
    idx = (np.abs(lambda_star - 0)).argmin()
    # lambda_star_final = lambda_star[idx]


    try:
        lambda_star_final = lambda_star_selected[0]
    except:
        idx = (np.abs(lambda_star - 0)).argmin()
        lambda_star_final = np.abs(lambda_star[idx])
        # result = np.zeros(3)
        # return result
    try:
        result = inv((A.T @ invPsi @ A + lambda_star_final * P)) @ (A.T @ invPsi @ b - (lambda_star_final/2) * q)
    except:
        result = np.linalg.pinv((A.T @ invPsi @ A + lambda_star_final * P)) @ (A.T @ invPsi @ b - (lambda_star_final/2) * q)
    # print(result[0:3].flatten())
    return result[0:3].flatten()
    # return theta[0:3, minIndex].flatten()


def estimate_xyz_ChuengPara(r):
    speaker_x_coords = np.array([0.5, 1.015, 5.183, 6.901])
    speaker_y_coords = np.array([0.05, 3.950, 0.067, 3.948])
    speaker_z_coords = np.array([0.146, 2.215, 0.744, 1.322])

    S = np.transpose(np.vstack((speaker_x_coords, speaker_y_coords, speaker_z_coords)))
    N = 4
    eye = np.eye(N)
    A = np.hstack((S, -0.5 * np.ones((N, 1))))
    b = 0.5 * np.sum(np.power(S, 2), axis=1) - 0.5 * np.power(r, 2)
    b = b[:, np.newaxis]
    r_matrix = np.reshape(r, (N, 1))
    Psi = r_matrix @ r_matrix.T * eye
    invPsi = inv(Psi)
    P = np.diag([1, 1, 1, 0])
    q = np.array((0, 0, 0, -1))[:, np.newaxis]

    [L, U] = np.linalg.eig((inv(A.T @ invPsi @ A) @ P))
    z = np.sort(L)[::-1]
    si = np.argsort(L)[::-1]
    U2 = U[:, si]
    c = (U2.T @ q).flatten()
    g = (inv(U2) @ inv((A.T @ invPsi @ A)) @ q).flatten()
    e = ((invPsi @ A @ U2).T @ b).flatten()
    f = (inv(U2) @ inv((A.T @ invPsi @ A)) @ A @ invPsi @ b).flatten()

    # solve the five root equation
    lam = sy.symbols('lam')
    expr = c[3] * f[3] \
           - (lam / 2) * c[3] * g[3] \
           + ((c[2] * f[2]) / (1 + lam * z[2])) + ((c[1] * f[1]) / (1 + lam * z[1])) + (
                       (c[0] * f[0]) / (1 + lam * z[0])) \
           - (lam / 2) * (((c[2] * g[2]) / (1 + lam * z[2])) + ((c[1] * g[1]) / (1 + lam * z[1])) + (
                (c[0] * g[0]) / (1 + lam * z[0]))) \
           + ((e[2] * f[2] * z[2]) / ((1 + lam * z[2]) ** 2)) + ((e[1] * f[1] * z[1]) / ((1 + lam * z[1]) ** 2)) + (
                       (e[0] * f[0] * z[0]) / ((1 + lam * z[0]) ** 2)) \
           - (lam / 2) * ((((e[2] * g[2] + c[2] * f[2]) * z[2]) / (1 + lam * z[2]) ** 2) + (
                ((e[1] * g[1] + c[1] * f[1]) * z[1]) / (1 + lam * z[1]) ** 2) + (
                                      ((e[0] * g[0] + c[0] * f[0]) * z[0]) / (1 + lam * z[0]) ** 2)) \
           + ((lam ** 2) / 4) * (((c[2] * g[2] * z[2]) / (1 + lam * z[2]) ** 2) + (
                (c[1] * g[1] * z[1]) / (1 + lam * z[1]) ** 2) + ((c[0] * g[0] * z[0]) / (1 + lam * z[0]) ** 2))

    lambda_star = np.array(list(sy.solveset(expr, lam,  domain= sy.Reals)), dtype=np.float_)
    fval = np.zeros(len(lambda_star))
    theta = np.zeros((4, len(lambda_star)))
    for i in range(len(lambda_star)):
       try:
           theta[:,i] = (inv((A.T @ invPsi @ A + lambda_star[i] * P)) @ (A.T @ invPsi @ b - (lambda_star[i]/2) * q)).flatten()
           fval[i] = ((A @ theta[:,i])[:, np.newaxis] - b).T @ invPsi @ ((A @ theta[:,i])[:, np.newaxis] - b)
       except:
           fval[i] = np.infty
    minIndex = np.argmin(fval)

    # result = theta[0:3, minIndex].flatten()
    # lambda_star_selected = lambda_star[lambda_star > 0]
    # idx = (np.abs(lambda_star - 0)).argmin()
    # lambda_star_final = lambda_star[idx]

    # try:
    #     lambda_star_final = lambda_star_selected[0]
    # except:
    #     result = np.zeros(3)
    #     return result
    # try:
    #     result = inv((A.T @ invPsi @ A + lambda_star_final * P)) @ (A.T @ invPsi @ b - (lambda_star_final/2) * q)
    # except:
    #     result = np.linalg.pinv((A.T @ invPsi @ A + lambda_star_final * P)) @ (A.T @ invPsi @ b - (lambda_star_final/2) * q)
    # print(result[0:3].flatten())
    return theta[0:3, minIndex].flatten()


def estimate_xyz_GaussNewton(S, N, r):
    def residual_toa(x, r, S, eye):
        [n, dim] = S.shape
        R = np.tile(x, (n, 1)) - S
        ranges = np.sqrt(np.sum(np.power(R, 2), axis=1))
        f = ranges - r
        J = R / np.transpose([ranges] * dim)
        W = inv(sp.linalg.sqrtm(eye))
        f = W @ f
        J = W @ J
        return [f, J]

    eye = np.eye(N)
    D = np.hstack((-np.ones((N - 1, 1)), np.eye((N - 1))))
    A = D @ S
    B = D @ (np.sum(np.power(S, 2), axis=1) - r ** 2) / 2
    x0 = np.linalg.lstsq(A, B, rcond=None)[0]
    maxIterations = 8
    tolResult = 0.001
    x = x0

    for i in range(maxIterations):
        [f, J] = residual_toa(x, r, S, eye)
        dx = np.linalg.lstsq(-J, f, rcond=None)[0]
        x[:] = x[:] + dx
        if np.linalg.norm(dx, ord=2) < tolResult:
            break
    return x.flatten()

def estimate_xyz_GaussNewton_reg(S, N, r):
    def residual_toa_reg(x, r, S, eye):
        [n, dim] = S.shape
        R = np.tile(x, (n, 1)) - S
        ranges = np.sqrt(np.sum(np.power(R, 2), axis=1))
        f = ranges - r
        J = R / np.transpose([ranges] * dim)
        W = inv(sp.linalg.sqrtm(eye))
        #add regularisation terms
        k = 1*10**(-4)
        test1 = (W @ f)
        test2 = np.array(k*(x-np.sum(S)/n)).T
        f = np.concatenate(((W @ f), np.array(k*(x-np.sum(S)/n)).T))[:, np.newaxis]
        J = np.vstack(((W @ J), np.array(k*(np.eye(dim)))))
        return [f, J]


    eye = np.eye(N)
    D = np.hstack((-np.ones((N - 1, 1)), np.eye((N - 1))))
    A = D @ S
    B = D @ (np.sum(np.power(S, 2), axis=1) - r ** 2) / 2
    x0 = np.linalg.lstsq(A, B, rcond=None)[0]
    maxIterations = 8
    tolResult = 0.01
    x = x0
    for i in range(maxIterations):
        [f, J] = residual_toa_reg(x, r, S, eye)
        dx = np.linalg.lstsq(-J, f, rcond=None)[0].flatten()
        x[:] = x[:] + dx
        if np.linalg.norm(dx, ord=2) < tolResult:
            break
    return x.flatten()

