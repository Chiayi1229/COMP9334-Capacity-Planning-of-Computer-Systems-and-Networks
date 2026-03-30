#############################################################################################
#                                                                                           #
#         M/M/m system simulation                                                           #
#         usage : simulate(m: int, lambd: float, mu: float, step: int)                      #
#         m : server_num , lambda : arrival_rate , mu : service_rate step : steps number    #
#                                                                                           #
#############################################################################################

import random
import math
import time

#total_time = int(input("Enter time for simulation (Hours): "))
#print(total_time)
m = 1   # server num
Q = 0
qu = []     #event list Queue
eventTime = []
eventNum = 0
ArrivalTime = []
FinishTime = []
ServiceTime = []

def RandomTime(timeStamp: float, rate: float , trigger: bool):
    x = random.uniform(0.0,1.0)
    RandomTime = math.log(1-x)/-rate
    if(trigger == True):
        global ServiceTime
        ServiceTime.append(RandomTime)
    timeStamp+=RandomTime
    return timeStamp
    
def Initialize(lambd: float,server_num: int): 
    global B
    global qu
    global Q
    global eventNum
    global ArrivalTime
    global m
    
    Q = 0
    B = False
    m = server_num
    t = RandomTime(time.time(),lambd,False)
    qu.append('A')
    eventTime.append(t)
    ArrivalTime.append(t)
    #print("----------Initialize---------")
    #print("TimeQ",eventTime)
    #print("EventQ",qu)
    
def order(et: float,symbol: chr):
    num=0
    for x in range(eventNum+1,len(qu)):
        if(et>eventTime[x]):
            #print("switch")
            num+=1
    eventTime.insert(eventNum+1+num, et)
    qu.insert(eventNum+1+num, symbol)
    #print("TimeQ",eventTime)
    #print("EventQ",qu)
    
def ArrivalEvents(lambd: float, mu: float):
    global B
    global qu
    global Q
    global eventNum
    global ArrivalTime
    global FinishTime
    #print("----------Arrival------------")
    if ( B == False):
        B = True
        t_Finish = RandomTime(eventTime[eventNum],mu,True)
        order(t_Finish,'F')
        FinishTime.append(t_Finish)
    else:
        Q += 1
        
    t_Arrival = RandomTime(eventTime[eventNum],lambd,False)
    order(t_Arrival,'A')
    ArrivalTime.append(t_Arrival)

def FinishServiceEvents(mu: float):
    global B
    global qu
    global Q
    global eventNum
    global FinishTime
    #print("----------Finish------------")
    if ( Q > 0):
        if ( Q+1 > m ):
            mu = mu*m
        else :
            mu = mu*(Q+1)
        Q -=1
        t_Finish = RandomTime(eventTime[eventNum],mu,True)
        order(t_Finish,'F')
        FinishTime.append(t_Finish)
    else:
        B = False
    
def calRSTime():
    sum = 0
    for i in range(len(FinishTime)):
        tmp = FinishTime[i] - ArrivalTime[i]
        sum = sum + tmp
    avg_RST = sum/len(FinishTime)
    return avg_RST

def calWTime():
    sum = 0
    for i in range(len(FinishTime)):
        Rst = FinishTime[i] - ArrivalTime[i]
        Wt = Rst - ServiceTime[i]
        sum = sum + Wt
    avg_WT = sum/len(FinishTime)
    return avg_WT
    
def simulate(m: int, lambd: float, mu: float, step: int): # m : num of server , lambd : arrival_rate , mu : service_rate
    global B
    global qu
    global Q
    global eventNum
    Initialize(lambd,m)
    global eventNum
    while eventNum < step :
        if (qu[eventNum]=="A"):
            ArrivalEvents(lambd, mu)
        elif (qu[eventNum]=="F"):
            FinishServiceEvents(mu)
        else:
            print("erro")
        eventNum+=1
        
    avg_RST = calRSTime()
    avg_WT = calWTime()
    
    return avg_WT, avg_RST;

avg_WT, avg_RST = simulate(5,1,5,100000)
# m : num of server , lambd : arrival_rate , mu : service_rate
print("avg_WT =",avg_WT)
print("avg_RST =",avg_RST)
