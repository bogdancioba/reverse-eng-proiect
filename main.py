import os
import shutil
import sys
import time

import detmap as Detections
import scan as Scan

def validate_detection(raw_name, detection):
    points = 0
    expected_detection = set()
    detection_file = raw_name + ".result"
    fd = open(detection_file, "rb")
    msg = ""

    try:
        bt = bytearray(fd.read())
        for x in bt:
            det = Detections.Detection(x)
            expected_detection |= { det }
    except Exception as e:
        print(e)
        points = 0
    finally:
        fd.close()

    max_points = len(expected_detection)
    points = max_points - len(detection ^ expected_detection)

    if (points != max_points):
        msg = "Error scanning %s.bender.\n"%(raw_name)
        msg += "Expected " + str(expected_detection) + " but got " + str(detection)

    return (points, max_points, msg)

def run_test(scanner, test_folder, temp_folder):
    local_score = 0
    max_score   = 0
    scan_time   = 0.0
    idle_time   = 0.0

    for root, directories, files in os.walk(test_folder):
        for name in files:
            full_name = os.path.join(root, name)
            raw_name, file_extension = os.path.splitext(full_name)

            if (file_extension == ".bender"):
                try:
                    print("Scanning " + full_name)
                    scan_path = os.path.join(temp_folder, "sample.bender")
                    start = time.time()
                    # Maybe we should use a simple function that copies (or reads) one byte at a time.
                    shutil.copy2(full_name, scan_path)
                    copy_duration = time.time() - start

                    start = time.time()
                    detection = scanner.scan(scan_path)
                    scan_duration = time.time() - start

                    success = False

                    if (len(detection)):
                        file_score, max_file_score, error_message = validate_detection(raw_name, detection)
                        max_score += max_file_score

                        success = (file_score == max_file_score)

                        if (file_score > 0):
                            local_score += file_score
                        else:
                            print(error_message)

                    os.unlink(scan_path)

                    if (success == True):
                        scan_time += scan_duration
                        idle_time += copy_duration

                    print("\tSuccess: %r, Idle duration %.6lf, Scan duration %.6lf"%(success, copy_duration, scan_duration))
                except Exception as e:
                    print(e)
                    pass

    return local_score, max_score, scan_time, idle_time

def main():
    scanner     = Scan.MyScanner()
    ret         = False
    score       = 0
    max_score   = 0
    scan_time   = 0.0
    idle_time   = 0.0
    overhead    = 0.0
    temp_folder = "tmp"

    os.makedirs(temp_folder, exist_ok = True)
    temp_folder_path = os.path.abspath(temp_folder)

    try:
        ret = scanner.init()
    except:
        print("Failed to initialize scanner. Exiting...")
    finally:
        if (ret == False):
            sys.exit()

    for i in range(1, 3):
        test_folder = "in_0" + str(i)
        if (os.path.exists(test_folder) == False):
            break
        
        s, m, st, it = run_test(scanner, os.path.abspath(test_folder), temp_folder_path)
        score     += s
        max_score += m
        scan_time += st
        idle_time += it

    scanner.uninit()
    
    if (score and idle_time):
        overhead = (scan_time / idle_time - 1) * 100.0

    print("Score = %d/%d, Overhead = %.6lf%%"%(score, max_score, overhead))

    os.rmdir(temp_folder_path)
    return

if __name__ == "__main__":
    main()