'''DICHOTOMOUS STATISTICS ARE OBTAINED BY THIS CODE WITH AN EXISTING .NPY FILE (NUMPY ARRAY)'''
import numpy as np

output_array = np.load("thedata.npy")

hits = output_array[0,:,:] #HITS AS ARRAY
misses = output_array[1,:,:] #MISSES AS ARRAY
false_a = output_array[2,:,:]#FALSE ALARMS AS ARRAY
correct_n = output_array[3,:,:] #CORRECT NEGATIVES AS ARRAY
h = np.sum(hits)
m = np.sum(misses)
f = np.sum(false_a)
c = np.sum(correct_n)

pod = h/(h+m)
print('Probability of detection: {}'.format(pod))
#False alarm ratio:

far = f/(h+ f)
print('False alarm ratio: {}'.format(far))
# Probability of false detection:

pofd = f/(f+c)
print('Probability of false detection: {}'.format(pofd))
# Accuracy: • ACC = (A+D)/(A+B+C+D)

acc = (h+c)/ (h+m+c+f)
print('Accuracy: {}'.format(acc))
# Critical success index:
# • CSI = A/(A+B+C)

csi = h/(h+f+m)
print('Critical success index: {}'.format(csi))

# Heidke skill score:
# • HSS = 2(AD-BC) / [(A+C)(C+D) + (A+B)(B+D)]

hss = 2* (h*c - m*f)/ ((h+ m)*(m + c)+ (h+f) + (f+ c))

print('Heidke skill score: {}'.format(hss))
