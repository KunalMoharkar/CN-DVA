import sys
import math
from threading import Thread, Lock
from Buffer import *
from Network import *
from Router import *
import time

LOCK = Lock()


def thread_target(network,buffer,r):

    for i in range(4):
        
        

        with LOCK:
            print(f"Itreation number : {i+1}")
            print(f"Table for router {r.name}")
            r.show_details()
            r.initialize_mod()

        forward_dv_to_neighbours(network,buffer,r)
        #sleep thread for 2 sec
        time.sleep(2)
        
        #proceed only when all neighbours received
        while buffer.all_neighbours_received(r) == False:
            pass

        get_tables_from_buffer(buffer,r)

        #with LOCK:
        #    print(f"Thread for router {r.name}")
        #    r.show_details()


def bellman_ford(router,dv_list):

    num_routers = len(router.dv)

    for i in range(num_routers):

        for x in dv_list:

            for r_dv in router.dv:

                if r_dv[0] == x[0]:

                    val = r_dv[1]

            val = val + x[1][i][1]

            if val < (router.dv[i][1]):

                router.dv[i][1] = val
                router.modified[i] = 1

       

def get_tables_from_buffer(buffer, router):

        with LOCK:
            for x in buffer.queue:
                if x[0] == router.name:

                    dv_list = []
                    values = len(x[1])
                    for i in range(values):
                        dv_list.append(x[1].pop(0))

        bellman_ford(router, dv_list)
    

def forward_dv_to_neighbours(network, buffer, router):
    
        for n in router.neighbours:
            r = network.get_router_by_name(n)
            with LOCK:
                buffer.insert_buffer(router, r)


        
def initialize_dv(network,router_names, edge_list, router_list):

    for router in router_list:


        dv = []

        for r in router_names:
            
            if r == router.name:
                dv.append([r,0])
            else:
                dv.append([r,math.inf])

        router.dv = dv

    for edge in edge_list:

        u = network.get_router_by_name(edge[0])
        v = network.get_router_by_name(edge[1])

        u.update_dv_value(edge[1], int(edge[2]))
        v.update_dv_value(edge[0], int(edge[2]))


def initialize_neighbours(router_names, edge_list):

    router_list = [] 
    for router in router_names:

        rt = Router(router,[],[])
        
        for edge in edge_list:

            if edge[0] == router:

                rt.neighbours.append(edge[1])
        
        for edge in edge_list:

            if edge[1] == router:

                rt.neighbours.append(edge[0])

        router_list.append(rt)

    
    return router_list

def scan_input(filename):

    #open the file
    f = open(filename, "r")
    #first line has number of routers
    num_routers = f.readline()
    router_names = f.readline()
    router_names = router_names.split()

    edge_list = []

    #read the  next lines till EOF
    for x in f:

        if x == 'EOF':
            break
        
        x = x.split()

        edge_list.append(x)

    #close file
    f.close()

    return router_names, edge_list


if __name__ == "__main__":

    #file name passed in cmd args
    filename =  sys.argv[1]
    router_names, edge_list = scan_input(filename)
    router_list = initialize_neighbours(router_names,edge_list)
    network = Network(router_list)
    initialize_dv(network, router_names, edge_list, router_list)
    print("-------------------INITIAL NETWORK -----------------------")
    network.initialize_modified()
    network.show_details()
    buffer = Buffer(router_names)
   
    start = time.time()

    flag = 0
    it = 1

    threads = []

    for router in router_names:
        r = network.get_router_by_name(router)
        th = Thread(target=thread_target,args=(network,buffer,r ))
        threads.append(th)

    for th in threads:
        th.start()

    for th in threads:
        th.join()


'''
    while True: 
            print(f"----------------------------------------------------------------------------------------------")
            print(f"\nItreation count: {it} ")
            it = it + 1

            threads = []
            
            for router in router_names:
                r = network.get_router_by_name(router)
                th = Thread(target=thread_target,args=(network,buffer,r ))
                threads.append(th)

            for th in threads:
                th.start()

            #wait for threads to end
            for th in threads:
                th.join()

            
            network.show_details()
            network.initialize_modified()

            #check if converged and break

            if network.check_if_coverged():

                flag  = flag + 1

                if flag == 3:

                    break 
'''

    

  



