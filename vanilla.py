import os
import heapq
import tempfile
import shutil
import csv

def sort_large_file(input_file, output_file, chunk_size=5000, first_name_col=2):
    temp_dir = tempfile.mkdtemp()
    chunk_files = []
    try:
        with open(input_file, 'r', newline='') as f:
            header = next(f).strip()
            reader = csv.reader(f)
            chunk = []
            count = 0
            
            for row in reader:
                if len(row) > first_name_col: 
                    chunk.append(row)
                    count += 1
                
                if count >= chunk_size:
                    chunk.sort(key=lambda x: x[first_name_col])
                    chunk_path = f"{temp_dir}/chunk_{len(chunk_files)}.csv"
                    
                    with open(chunk_path, 'w', newline='') as chunk_file:
                        writer = csv.writer(chunk_file)
                        writer.writerows(chunk)
                    
                    chunk_files.append(chunk_path)
                    chunk = []
                    count = 0
            
            if chunk:
                chunk.sort(key=lambda x: x[first_name_col])
                chunk_path = f"{temp_dir}/chunk_{len(chunk_files)}.csv"
                
                with open(chunk_path, 'w', newline='') as chunk_file:
                    writer = csv.writer(chunk_file)
                    writer.writerows(chunk)     
                chunk_files.append(chunk_path)
        
        with open(output_file, 'w', newline='') as out:
            writer = csv.writer(out)
            writer.writerow(header.split(','))
            files = [open(f, 'r', newline='') for f in chunk_files]
            readers = [csv.reader(f) for f in files]
            heap = []

            for i, reader in enumerate(readers):
                try:
                    row = next(reader)
                    if row:
                        heapq.heappush(heap, (row[first_name_col], row, i))
                except StopIteration:
                    pass

            while heap:
                _, row, i = heapq.heappop(heap)
                writer.writerow(row)         
                try:
                    next_row = next(readers[i])
                    if next_row:
                        heapq.heappush(heap, (next_row[first_name_col], next_row, i))
                except StopIteration:
                    pass
            for f in files:
                f.close()
    
    finally:
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    chunk_size = int(sys.argv[3]) if len(sys.argv) > 3 else 5000
    
    sort_large_file(input_file, output_file, chunk_size)
    print(f"Sort complete: {output_file}")