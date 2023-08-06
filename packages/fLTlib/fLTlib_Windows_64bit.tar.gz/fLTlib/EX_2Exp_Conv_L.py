# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#    This file demos how to fit EXP curve convolute with any device response function using the C/C++ finite Legendre transform
#    library, fLTlib, and its help functions in fLTHelpFun.py
#
#    For more information on fLTlib, please use Help(fLTlib)
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
from   fLTHelpFun        import *
import matplotlib.pyplot as plt

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#    Read the test data. It contains time, system device response function, and two demo curves.
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
filename = 'TEST_With_Device_Responce_Function.csv'
my_data = myCSVRead(filename, 1)
x_time, y_Response = my_data[:,0], my_data[:,1]
#print np.shape(my_data)

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#    Here we prepare the base array with the given Response function
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
nn = 8      # number of components in L-domain
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#
#    Calculate the base array.
#    *Note: This can be used for all curves of the same y_Response
#
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
fP = myGetBase(y_Response, nn)
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#    fp can be used for all curves of the same y_Response
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =


# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#    Here we prepare the fitting start values:
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
Tm = x_time[-1]

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#    Tm is the last time point, and we use a very easy guess based on Tm:
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#            A1  Tau1   A2  Tau2  Offset
Fit_Start = [0,  Tm/10, 0,  Tm/5, 0      ]  # We use a very easy start guess

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#    Now we use a loop to fit two curves:
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
for ii in range(2, 4):
    # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    #    Get the data
    # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    y_T1 = my_data[:,ii]

    # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    #    We fit for 2 EXP functions, Output is: [Chi, n, A_ll, A_err]
    # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    Out = myExpFit_Conv_LL2(y_T1,  fP, Tm, [1, 1, 1, 1, 1], Fit_Start) # same as: Chi, n, A_ll, A_err = ...
    #print Out[2]

    # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    #    We also fit for 1 EXP, Output is: [Chi, n, A_ll, A_err]
    #    Same as: myExpFit_Conv_LL2(y_T1,  fP, Tm, [1, 1, 0, 0, 1], Fit_Start)
    # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    Out1 = myExpFit_Conv_LL(y_T1,  fP, Tm)
    #print Out1[2]

    # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    #    We check the result by generating the EXP curve and convoluting with the system response function
    # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    AT1, E1 = Out1[2], Out1[3];
    Y1 = myEXPCal(x_time, AT1)   # Now we calculate the exp curve with the real X
    Y1 = myConv(Y1, y_Response)  # Now we convolute the exp with the response function
    AT2, E2 = Out[2], Out[3]
    Y2 = myEXPCal(x_time, AT2)   # Now we calculate the exp curve with the real X
    Y2 = myConv(Y2, y_Response)  # Now we convolute the exp with the response function

    # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    #    Plot the result
    # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    plt.figure('L'+str(ii-1))

    # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    # Display the result for Single Exp Fit:
    # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    ax = plt.subplot2grid((4,2), (0, 0), rowspan=3)
    plt.plot(x_time, y_Response,  x_time, y_T1, x_time, Y1 );
    plt.text(0.2, 0.88, 'L-Domain, Single Exp Fit', transform=ax.transAxes)
    plt.text(0.2, 0.80, 'A1=' + str(myRound(AT1[0],4))+'+/-' + str(myRound(E1[0],4)), transform=ax.transAxes)
    plt.text(0.2, 0.75, 'T1=' + str(myRound(AT1[1],4))+'+/-' + str(myRound(E1[1],4)), transform=ax.transAxes)
    #plt.text(0.2, 0.70, 'A2=' + str(myRound(AT1[2],4))+'+/-' + str(myRound(E1[2],4)), transform=ax.transAxes)
    #plt.text(0.2, 0.65, 'T2=' + str(myRound(AT1[3],4))+'+/-' + str(myRound(E1[3],4)), transform=ax.transAxes)
    plt.text(0.2, 0.60, 'Offset=' + str(myRound(AT1[4],4))+'+/-' + str(myRound(E1[4],4)), transform=ax.transAxes)
    plt.subplot2grid((4,2), (3, 0))
    plt.plot(x_time, y_T1 - Y1 )
    ax.figure.canvas.draw()

    # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    # Display the result for Double Exp Fit:
    # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    plt.figure; ax = plt.subplot2grid((4,2), (0, 1), rowspan=3)
    plt.plot(x_time, y_Response,  x_time, y_T1, x_time, Y2 );
    plt.text(0.2, 0.88, 'L-Domain, Double Exp Fit', transform=ax.transAxes)
    plt.text(0.2, 0.80, 'A1=' + str(myRound(AT2[0],4))+'+/-' + str(myRound(E2[0],4)), transform=ax.transAxes)
    plt.text(0.2, 0.75, 'T1=' + str(myRound(AT2[1],4))+'+/-' + str(myRound(E2[1],4)), transform=ax.transAxes)
    plt.text(0.2, 0.70, 'A2=' + str(myRound(AT2[2],4))+'+/-' + str(myRound(E2[2],4)), transform=ax.transAxes)
    plt.text(0.2, 0.65, 'T2=' + str(myRound(AT2[3],4))+'+/-' + str(myRound(E2[3],4)), transform=ax.transAxes)
    plt.text(0.2, 0.60, 'Offset=' + str(myRound(AT2[4],4))+'+/-' + str(myRound(E2[4],4)), transform=ax.transAxes)
    plt.subplot2grid((4,2), (3, 1))
    plt.plot(x_time,y_T1 - Y2 )
    if ii<3:
        plt.ion()
    else:
        plt.ioff()
    plt.show()

