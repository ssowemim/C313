import math
import random
import sys

#   CMPUT 313 Assignment 1
#   Done By: Sonola Sowemimo & Abdullah Alghamdi


def arguments():
    #used to take in all user arguments, making the assumption user follows
    #the order of inputs
    if len(sys.argv) < 10:
        print ("Not enough parameters. Please re-enter parameters in the right format")
        exit()
    M = str(sys.argv[1]) # B or I
    A = int(sys.argv[2]) # Assume its 50 bit time units
    K = int(sys.argv[3]) # Explore K= 0, 1, 2, 10, 40, 100, 400, 1000
    F = int(sys.argv[4]) # Assume its 4000 bits
    e = float(sys.argv[5]) #vary this for e = 0.0001, 0.0003, 0.0005, 0.000, 0.001
    B = int(sys.argv[6]) # 0 independent model, burst - 50 & 500 bit
    N = int(sys.argv[7]) # 0 independent model, burst - 5000 & 1000 bit
    R= int(sys.argv[8]) #Should be seeds for the trial - 5,000,000
    T = int(sys.argv[9]) # This simulator T = 5
    seeds = []
    for i in range(T):
        seeds.append(int(sys.argv[9+1+i]))


    #checks to see if first argument is independent or burst
    #error thrown otherwise

    if M not in ['B','I'] :
        print ("ERROR! Please check your first argument.  \
Must be ( I for independent error) or (B for burst error)")
        exit()

    #checks if appropriate input are acciompanied with independent model
    if M == 'I':
        if (N or B) != 0:
            print ("ERROR! For Independent Error Mode, B and N must be assigned to Zero!")
            exit()

    #checks to see if appropiate number of input has been given
    if len(sys.argv) != 10+(T):
        print ("ERROR! Please re-enter your input in the corrent form. \
Note: the number of seeds = the number of trials (T).")
        exit()

    global parameters

    parameters = [M,A,K,F,e,B,N,R,T,seeds]
    return parameters

#   This is used to calculate the block size
def block_measure(K,F):
    if K >0:
        block_size = F/K
        return block_size
    else:
        block_size = 0
        return block_size

# This function is used to check the state of the bits in error
# checks for independent errors & burst errors
def check(initFrame,e, independent,N,B,totalBlock,parity):

    numErrors = 0
    m = 0
    if totalBlock== 0:
        totalBlock = len(initFrame)
    if B > 0:
        errorBusrt = e * ((B+N)/B)
    for i in range(len(initFrame)):
        if independent ==1:
            if initFrame[i] <= e:
                numErrors += 1
                if parity == 0:
                    return 0
                if numErrors > 2:
                    return 0
        if independent == 0:
            if initFrame[i] <= errorBusrt:
                numErrors += 1
                if parity == 0:
                    return 0
                if numErrors > 2:
                    return 0
        m += 1
        if m >= totalBlock:
            # re-initialize m
            m = 0
            numErrors = 0
    return 1

# This handles the stats for the simulation, specifically standard dev frames
def StandardDev_Frames(average_frame_tx, T, succesfull_frames, total_frames):
    x_bar = total_frames/succesfull_frames # where x_ber is the mean
    std = 0

    for t in range(T):
        std += ((average_frame_tx[t] - x_bar)**2)

    std = std/4
    std = math.sqrt(std)

    return std, x_bar

# Function to handle the standard deviation for the throughput
def StandardDev_Thro(average_throughput, T, succesfull_frames, total_time, F):
    x_bar = (succesfull_frames*F)/total_time
    std = 0
    for t in range(T):
        std += ((average_throughput[t] - x_bar)**2)
    std = std/4
    std = math.sqrt(std)
    return std, x_bar

# Handles the confidence intervals
def ConfidenceInts(x_bar, std,T):
    
    offset = (2.776 * (std/math.sqrt(T)))
    con1 = x_bar - offset;
    con2 = x_bar + offset;

    return con1, con2;


# Main function that runs the simulation
def main():
    # set the parameters from arguments
    parameters = arguments()
    M,A,K,F,e,B,N,R,T,seeds = parameters

    print ("\nSTART SIMULATION")

    # Print out user input, shows user values they put in
    print ("User Input: " +str(M) +" "+ str(A) +" "+str(K) +" "+ str(F) +" "+ str(e)+" "+str(B)+" "+str(N)+" "+str(R)+" "+str(T)+" "+str([i for i in seeds])+ "\n")

    # Measure the size of the block and parity check bit
    block_size = block_measure(K,F)
    if block_size>0:
        parity = int(math.log(block_size,2))
    else:
        parity = 0
    # Check if the type of error either I or B
    if M == "I":
        independent = 1
    else:
        independent = 0

    if K ==0:
        frame_size = F

    frame_size  = int(math.log(block_size, 2) if block_size>0 else 1)

    frame_size = frame_size * K
    frame_size += F

    # initialize important variables
    average_frame_tx = []
    average_throughput = []

    succesfull_frames = 0
    total_frames = 0
    total_time = 0

    for t in range(T):
        time = 0
        c = 0
        calculatedFrames  = 0
        random.seed(seeds[t])
        while (time <= R):
            initFrame =[0]*frame_size

            # if independent error
            if independent == 1:
                for i in range(frame_size):
                    initFrame[i] = random.random()
            # if burst error
            else:
                flag = 1
                for i in range(frame_size):

                    if flag ==1:
                        initFrame[i] = 1
                        c += 1
                        if c >= N:
                            flag =0
                            c = 0
                    if flag == 0:
                        initFrame[i] = random.random()
                        c += 1
                        if c >= B:
                            flag = 1
                            c = 0
            # now check for errors
            totalBlock = block_size+ parity
            errors = check(initFrame,e, independent,N,B,totalBlock,parity)

            if errors == 1:
                calculatedFrames += 1
            # Now increment time
            time += frame_size + A

        print("Trial Number: " + str(t+1))
        # calculate the trial stats
        if calculatedFrames ==0:
            print ("not received")
            average_frame_tx.append(0)
            average_throughput.append(0)
        else:
            average_frame_tx.append((time/(frame_size+A))/calculatedFrames)
            average_throughput.append((F*calculatedFrames)/time)

        succesfull_frames += calculatedFrames
        total_frames += time/(frame_size + A)
        total_time += time

    if succesfull_frames ==0 :
        print ("line 207")
        exit()

    # Calculating the stats, std devs, confidence intervals
    frames_std, x_bar_frames = StandardDev_Frames(average_frame_tx, T, succesfull_frames, total_frames)
    f_con1,f_con2 = ConfidenceInts(x_bar_frames, frames_std,T)
    throughput_std, x_bar_thro  = StandardDev_Thro(average_throughput, T, succesfull_frames, total_time, F)
    thro_con1,thro_con2 = ConfidenceInts(x_bar_thro , throughput_std,T)


    print ("\nAverage Frame Transmissions: " + str(total_frames/succesfull_frames) + " \nConfidence Intervals: (" + str(f_con1) + ", " + str(f_con2)+") " + "\n")
    print ("\nThroughput Average: " + str((F* succesfull_frames)/total_time) + "\nConfidence Intervals: (" + str(thro_con1) + ", " + str(thro_con2)+")" + "\n")
    print ("END SIMULATION\n")
main()
