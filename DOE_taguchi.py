import numpy as np
import template_DOE as doe


DataFile = open('Results_DOE_4_Var.txt','w')
DataFile.write('Iter\tAu0\tAl0\tAu1\tAl1\tt_spar\tt_spar_box\tt_rib\tt_skin\tn_ribs\tWeight\tLift\tDrag\tMaxMises\tDispTip\tEigenValue\tAlfa\n')
DataFile.close()

# AVar1 = np.linspace(0.1,0.9,num=5)
# AVar2 = np.linspace(0.1,0.9,num=5)
# AVar3 = np.linspace(0.5,0.6,num=5)
# AVar4 = np.linspace(-0.4,0.6,num=5)
# AVar5 = np.linspace(0.005,0.08,num=5)
# AVar6 = np.linspace(0.004,0.01,num=5)
# AVar7 = np.linspace(0.001,0.01,num=5)
# AVar8 = np.linspace(2,10,num=5)
AVar1 = np.linspace(0.16,0.35,num=5)       #Au0
AVar2 = np.linspace(0.1,0.3,num=5)      #Al0
AVar3 = np.linspace(0.16,0.4,num=5)     #Au1
AVar4 = np.linspace(-0.15,0.2,num=5)    #Al1
#AVar5 = np.linspace(0.001,0.01,num=5)   #t_spar
#AVar6 = np.linspace(0.002,0.02,num=5)   #t_spar_box
#AVar7 = np.linspace(0.002,0.01,num=5)   #t_rib
#AVar8 = np.linspace(0.0002,0.01,num=5)  #t_skin
#AVar9 = [10,13,16,19,22]        #n_ribs

Taguchi= [[1, 1, 1, 1, 1, 1],
        [1, 2, 2, 2, 2, 2],
        [1, 3, 3, 3, 3, 3],
        [1, 4, 4, 4, 4, 4],
        [1, 5, 5, 5, 5, 5],
        [2, 1, 2, 3, 4, 5],
        [2, 2, 3, 4, 5, 1],
        [2, 3, 4, 5, 1, 2],
        [2, 4, 5, 1, 2, 3],
        [2, 5, 1, 2, 3, 4],
        [3, 1, 3, 5, 2, 4],
        [3, 2, 4, 1, 3, 5],
        [3, 3, 5, 2, 4, 1],
        [3, 4, 1, 3, 5, 2],
        [3, 5, 2, 4, 1, 3],
        [4, 1, 4, 2, 5, 3],
        [4, 2, 5, 3, 1, 4],
        [4, 3, 1, 4, 2, 5],
        [4, 4, 2, 5, 3, 1],
        [4, 5, 3, 1, 4, 2],
        [5, 1, 5, 4, 3, 2],
        [5, 2, 1, 5, 4, 3],
        [5, 3, 2, 1, 5, 4],
        [5, 4, 3, 2, 1, 5],
        [5, 5, 4, 3, 2, 1],]

K=1
for w in range(len(Taguchi)):
# for w in range(len(Taguchi)-1):
    Var1 = float(AVar1[Taguchi[w][0]-1])
    Var2 = float(AVar2[Taguchi[w][1]-1])
    Var3 = float(AVar3[Taguchi[w][2]-1])
    Var4 = float(AVar4[Taguchi[w][3]-1])
#    Var5 = float(AVar5[Taguchi[w][5]-1])
#    Var6 = float(AVar6[Taguchi[w][6]-1])
#    Var7 = float(AVar7[Taguchi[w][7]-1])
#    Var8 = float(AVar8[Taguchi[w][8]-1])
#    Var9 = int(AVar9[Taguchi[w][9]-1])
#    print Var9				
    # Var1 = AVar1[Taguchi[w][1]-1]
    # Var2 = AVar2[Taguchi[w][2]-1]
    # Var3 = AVar3[Taguchi[w][3]-1]
    # Var4 = AVar4[Taguchi[w][4]-1]
    # Var5 = AVar5[Taguchi[w][5]-1]
    # Var6 = AVar6[Taguchi[w][6]-1]
    # Var7 = AVar7[Taguchi[w][7]-1]

#    Au0= 0.1710 #0.1954137884893201
#    Al0= 0.1362 #0.210499900574687
#    Au1= 0.3874 #0.297157861622602
#    Al1= -0.0942 #0.1150909342829381
    t_spar= 0.0068 #0.004473234920038927
    t_rib= 0.0046 #0.005127943532786699
    t_skin= 0.0018 #0.006486394197009234
    n_ribs= 19
    t_spar_box= 0.0061 #0.006531976101000104
#
#    genes={'Au0':Au0,'Al0':Al0,'Au1':Au1,'Al1':Al1,'t_spar':Var5,'t_spar_box':Var6,'t_rib':Var7,'t_skin':Var8,'n_ribs':Var9}

#    genes={'Au0':Var1,'Al0':Var2,'Au1':Var3,'Al1':Var4,'t_spar':Var5,'t_spar_box':Var6,'t_rib':Var7,'t_skin':Var8,'n_ribs':Var9}
    genes={'Au0':Var1,'Al0':Var2,'Au1':Var3,'Al1':Var4,'t_spar':t_spar,'t_rib':t_rib,'t_skin':t_skin,'t_spar_box':t_spar_box,'n_ribs':n_ribs}    
    Output = doe.Wing_model(genes)

    K+=1
    DataFile = open('Results_DOE_4_Var.txt','a')
    current_altitude='10000'  				
    DataFile.write('%i\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%i\t%.4f\t%.4f\t%.4f\t%.2f\t%.4f\t\t%.4f\t%.4f\n' % (K,genes['Au0'],genes['Al0'],genes['Au1'],genes['Al1'],genes['t_spar'],genes['t_spar_box'],genes['t_rib'],genes['t_skin'],genes['n_ribs'],Output['Weight'],Output['Lift'][current_altitude],Output['Drag'][current_altitude],Output['MaxMises'],Output['DispTip'],Output['EigenValue'],Output['alfas'][current_altitude]))        
    DataFile.close()
