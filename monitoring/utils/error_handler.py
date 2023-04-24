import subprocess

class ErrorHandler:

    @staticmethod
    def reset_lepton() -> bool:
        for i in range(2):
            process = subprocess.Popen('usbreset "PureThermal (fw:v1.3.0)"', shell=True, stdout=subprocess.PIPE, universal_newlines=True)
            process.wait()

            if  process.returncode == 0:
                process = subprocess.Popen('ls /dev/vid* | grep video0', shell=True, stdout=subprocess.PIPE, universal_newlines=True)
                process.wait()

                if  process.returncode == 0:
                    return True
                
        return False