import os
import tempfile
import pandas as pd
import sys
import shutil

def sort_large_file(input_file, output_file, memory_limit_gb = 12):
    chunk_files = []
    temp_dir = tempfile.mkdtemp()

    chunksize = int((memory_limit_gb * 1024 * 1024 * 1024) /5)
    chunk_count = 0
    for chunk in pd.read_csv(input_file, header= None, chunksize=chunksize, names=['name']):
        chunk_count += 1

        chunk_sorted = chunk.sort_values('name')

        chunk_file = os.path.join(temp_dir,f"chunk_{chunk_count}.csv")
        chunk_sorted.to_csv(chunk_file, index = False, header = False)
        chunk_files.append(chunk_file)

    sorted_chunks = (pd.read_csv(f, header=None, names=['name']) for f in chunk_files)
    pd.concat(sorted_chunks).sort_values('name').to_csv(output_file, index=False, header=False)

    shutil.rmtree(temp_dir)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Sorting The Names")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    memory_limit_gb = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    sort_large_file(input_file, output_file, memory_limit_gb)
    print(f"The sorted file is saved to {output_file}")
