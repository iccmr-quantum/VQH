import numpy as np

def adiabatic_interpolation(h1_file, h2_file, num_steps, output_file):
    # Load matrices from files
    h1 = np.genfromtxt(h1_file, delimiter=',')
    h2 = np.genfromtxt(h2_file, delimiter=',')
    
    # Extract step values from the header row
    h1_header = 'h1,s0,s1,s2,s3,s4,s5,s6,s7'
    h2_header = 'h1,s0,s1,s2,s3,s4,s5,s6,s7'
    #hd = ['h1','s0','s1','s2','s3','s4','s5','s6','s7']
    hd = ['h1','c','c#','d','d#','e','f','f#','g', 'g#', 'a', 'a#', 'b']
    #print(h1)
    #print(h1_header)
    # Interpolate matrices
    interpolated_matrices = []
    for step in range(num_steps):
        s_i = step / (num_steps - 1)  # Interpolation parameter
        interpolated_matrix = (1 - s_i) * h1 + s_i * h2
        interpolated_matrices.append(interpolated_matrix)
    
    #print(interpolated_matrices)

    # Save interpolated matrices to file
    with open(output_file, 'w') as f:
        # Write headers
        #f.write(','.join(str(h1_header)) + '\n')
        #f.write('h1,s0,s1,s2,s3,s4,s5,s6,s7'+'\n')
        
        for i, matrix in enumerate(interpolated_matrices):
            #f.write('h' + str(i + 1) + ',')
            #f.write(','.join(str(h1[0, 1:])) + '\n')  # Write step values
            #f.write('h1,s0,s1,s2,s3,s4,s5,s6,s7'+'\n')
            f.write('h1,c,c#,d,d#,e,f,f#,g,g#,a,a#,b'+'\n')
            for j in range(matrix.shape[0]):
                f.write(str(hd[j+1]) + ',')
                f.write(','.join([str(val) for val in matrix[j]]) + '\n')

# Example usage
h1_file = 'h1.csv'
h2_file = 'h2.csv'
num_steps = 5
output_file = 'h_setup.csv'

adiabatic_interpolation(h1_file, h2_file, num_steps, output_file)

