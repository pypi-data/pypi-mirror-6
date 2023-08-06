import numpy   as np
import fLTlib

# To calculate the EXP curve
def myEXPCal(X, A):
    return A[0]*np.exp(-X/A[1]) + A[2]*np.exp(-X/A[3]) + A[4]

# To calculate A and T for [0, Time_end], 
def myEXPBackCal(A_lm, Tm, n):
    return [A_lm[0]*np.exp(-1/A_lm[1]),  A_lm[1]*Tm/(n-1), A_lm[2]*np.exp(-1/A_lm[3]),  A_lm[3]*Tm/(n-1), A_lm[4]];

# To calculate A and T for [1, number of points]
def myEXPForeCal(A, Tm, n):
    A=np.double(A);
    return [A[0]/np.exp(-Tm/A[1]/(n-1)), A[1]/Tm*(n-1),    A[2]/np.exp(-Tm/A[3]/(n-1)), A[3]/Tm*(n-1),    A[4]];

def myConv(A, B):
    return np.abs(np.fft.ifft(np.fft.fft(A)*np.fft.fft(B)))

def myCSVRead(fn, skip):
    fHandle = open(fn,"rb")
    Out = np.loadtxt(fHandle,delimiter=",",skiprows=skip)
    fHandle.close()
    return Out

def myRound(d, n):
    return float(int(d*10**n))/10**n

# LM fit
# Starting Value
def myEXPStart(Y): # return EXP fit starting    
    if len(Y) > 50:
        A =[(Y[0]+Y[9]+Y[18])/4, 0, 0, 0, Y[-1]]
        T=[10, min(400, len(Y))]        
        if (Y[T[0]] - Y[T[0]+10]) != 0:
            A[1]= abs(10*(Y[T[0]+5]-A[4])*(T[0]+5)/(Y[T[0]] - Y[T[0]+10]))**0.5
            A[3]= A[1]*2
        elif (Y[T[0]] - Y[T[0]+30]) != 0:
            A[1]= abs(10*(Y[T[0]+5]-A[4])*(T[0]+5)/(Y[T[0]] - Y[T[0]+30]))**0.5
            A[3]= A[1]*2
        else:
            A[1] = len(Y)/10
            A[3]= A[1]*5
    else:
        A = [(Y[0]+Y[1]+Y[2])/4, len(Y)/10, 0, len(Y)/4, Y[-1]]  
    return A

def myGetBase(R, nn):
    nl = [R.shape[0],   nn]                      #points, facts
    P, X = fLTlib.myLegendre_P(nl[0], nl[1])        #generate spectrum
    fP = np.fft.ifft(np.fft.fft(P)*np.tile(np.fft.fft(R),[nn,1]))       #generate orthogonal base for unmixing
    return fP.real

def myExpFit_Conv_LL2(Y, fP, Tm, Sw, St):
    #Unmixing
    Chi, A, Error, Left = fLTlib.myUnmixing(Y, fP)
    #From Matlab when nn = 10
    #Chi = 995.4609382253686
    #A   = 0.0104971133311030    -0.0267258937158511    0.0320444692561389    -0.0277427502510529    0.0192173957050019
    #-0.0111387733775431    0.00556818359626335    -0.00240712589286962    0.000936818933682989    -0.000311491304475054
    #Error = 2.65309754742293e-12    8.96831276126106e-12    1.40934029125088e-11    2.17047658230039e-11    2.55155150698402e-11
    #3.50432044456513e-11    3.74052014158000e-11    4.86895431251074e-11    4.99414646691591e-11    6.21289371531480e-11
    return fLTlib.myFitEXP_LL(A, Tm, Sw, St) # same as, Chi, n, A_ll, A_err = ...

def myExpFit_Conv_LL(Y, fP, Tm):
    Chi, A, Error, Left = fLTlib.myUnmixing(Y, fP)
    Out = fLTlib.myFitEXP_LL(A, Tm, [1, 1, 0, 0, 1], [0, Tm/10, 0, Tm/5, 0]) # same as, Chi, n, A_ll, A_err = ...
    Out[2][3]=Out[2][1];
    return Out

def myCorrectError(AT0, AT1, E):
    Out = E
    nn  = E.shape[0]
    # We correct the error
    for ii in range (0, nn):
        if AT0[ii]<>0:
            Out[ii] = AT1[ii]/AT0[ii]*E[ii]
    return Out
    
    
def myExpFit_Conv_TT2(Y, R, Tm, Sw, St):
    nn = R.shape[0]
    # Before fit, we need to re-calculate Tau for an X-axes start from 1 end with number of points 
    A0 = myEXPForeCal(St, Tm, nn)
    Chi, n, AT, E = fLTlib.myFitEXP_LM_Conv(Y, R, Sw, A0)
    # After fit, we need to re-calculate Tau for the real X 
    AT1 = myEXPBackCal(AT, Tm, nn)
    # We correct the error
    E = myCorrectError(AT, AT1, E)
    return Chi, n, AT1, E

def myExpFit_Conv_TT(Y, R, Tm):
    nn = R.shape[0]
    # Fefore fit, we need to re-calculate Tau for an X-axes start from 1 end with number of points
    St = [0, Tm/10, 0.0, Tm/5, 0]
    A0 = myEXPForeCal(St, Tm, nn)
    Chi, n, AT, E = fLTlib.myFitEXP_LM_Conv(Y, R, [1, 1, 0, 0, 1], A0)
    AT[3]=AT[1]
    # After fit, we need to re-calculate Tau for the real X 
    AT1 = myEXPBackCal(AT, Tm, nn)
    # We correct the error
    E = myCorrectError(AT, AT1, E)
    return Chi, n, AT1, E



'''
Help on module fLTlib:

NAME
    fLTlib

FILE
    fltlib.so

FUNCTIONS
    myFitEXP_LL(...)
        myFitEXP_LL(legendre_A, T_end, [Fit_Par_Switch], [Starting_Value])
        
        Chi, nRegresCount, Para, Error = myFitEXP_LL(legendre_A, T_end), Fit Legendre amplitude A with single EXP
        
        Chi, nRegresCount, Para, Error = myFitEXP_LL(legendre_A, T_end, [Fit_Par_Switch]),
                Fit_Par_Switch is 0 or 1, for [A1, Tau1, A2, Tau2, Offset]
                e.g. 
                Fit_Par_Switch = [1,1,1,1,1], Fit legendre_A with double EXP and offset
        
        Chi, nRegresCount, Para, Error = myFitEXP_LL(legendre_A, T_end, [Fit_Par_Switch], [Starting_Value]), Fit legendre_A with double EXP and offset
        
        The return value A and Tau apply to T=[0, ... T_end]
    
    myFitEXP_LM(...)
        myFitEXP_LM(Y)
        
        Chi, nRegresCount, Para, Error = myFitEXP_LM(Y), Fit Y with single EXP
        
        Chi, nRegresCount, Para, Error = myFitEXP_LM(Y, [Fit_Par_Switch]),
                Fit_Par_Switch is 0 or 1, for [A1, Tau1, A2, Tau2, Offset]
                e.g. 
                Fit_Par_Switch = [1,1,1,1,1], Fit Y with double EXP and offset
        
        Chi, nRegresCount, Para, Error = myFitEXP_LM(Y, [Fit_Par_Switch], [Starting_Value]), Fit Y with double EXP and offset
        
        The return value A and Tau apply to T=[1, 2, ... , n], to correct for 0 ~ T_end, please use myEXPBackCal(A, T_end, n)
    
    myFitEXP_LM_Conv(...)
        myFitEXP_LM_Conv(Y, R)
        
        Chi, nRegresCount, Para, Error = myFitEXP_LM_Conv(Y, R), Fit Y with single EXP converluting with R
        
        Chi, nRegresCount, Para, Error = myFitEXP_LM_Conv(Y, R, [Fit_Par_Switch]),
                Fit_Par_Switch is 0 or 1, for [A1, Tau1, A2, Tau2, Offset]
                e.g. 
                Fit_Par_Switch = [1,1,1,1,1], Fit Y with double EXP and offset converluting with R
        
        Chi, nRegresCount, Para, Error = myFitEXP_LM(Y, R, [Fit_Par_Switch], [Starting_Value]), Fit Y with double EXP and offset converluting with R
        
        The return value A and Tau apply to T=[1, 2, ... , n], to correct for 0 ~ T_end, please use myEXPBackCal(A, T_end, n)
    
    myLegendre_A(...)
        myLegendre_A(Y, n, P)
        
        Usage: A, Yf = myLegendre_P(Y, 5, P)
        
        Getting the first n component of Y
        
        Yf = (A'* P)'
        
        P[DIM1 DIM2], DIM2 = points, DIM1 = number of facts
    
    myLegendre_P(...)
        myLegendre_P(point_count, fact_count)
        
        Usage: P, X = myLegendre_P(100, 5)
        
        Getting the Legendre spectrum
    
    myUnmixing(...)
        myUnmixing(Y[n,1], Base[m,n])
        
        Chi, A, Error, Left = myUnmixing(Y, Base), Calculate the linear unmixing of Y using Base
        
        Chi, A, Error, Left, Inv = myUnmixing(Y, Base, 1), Inverse array is also output
                Y = Base * A + Left
'''