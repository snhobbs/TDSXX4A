# TDS 684A, TDS 744A & TDS 784A Oscilliscope Documentation & GPIB Control


## Quick Start
The GPIB control is in python connected with a ethernet-gpib bridge.

+ User Manual: https://raw.githubusercontent.com/snhobbs/TDS744A/master/documents/TDS744A_UserManual_4thEdition.pdf
+ Programming Guide: https://raw.githubusercontent.com/snhobbs/TDS744A/master/documents/tds744_programmer_manual.pdf
+ GPIB Bridge: Prologix GPIB-ETHERNET Controller (http://prologix.biz/gpib-ethernet-1.2-faq.html)

## Usage
```{sh}
tds_scope.py --address 4 --ip 10.231.231.128 --name 1s_triangular_sweep_10khz_1p5MHz take-data --sources CH2 --sources CH3
```

## Output
```
 # file_name: labamp_10khz_10mhz_swept_sine                                                                                                                                                             
 # date: 2022-10-10                                                                                                                                                                                     
 # time: 12:58:26.045481                                                                                                                                                                                
 # BYT_NR : 2                                                                                                                                                                                           
 # BIT_NR : 16                                                                                                                                                                                          
 # ENCDG : ASC                                                                                                                                                                                          
 # BN_FMT : RP                                                                                                                                                                                          
 # BYT_OR : MSB                                                                                                                                                                                         
 # CH2:WFID : "Ch2, DC coupling, 5.000 Volts/div, 50.00ms/div, 15000 points, Pk Detect mode"                                                                                                            
 # NR_PT : 15000                                                                                                                                                                                        
 # PT_FMT : Y                                                                                                                                                                                           
 # XUNIT : "s"                                                                                                                                                                                          
 # XINCR : 1.000E-3                                                                                                                                                                                     
 # XZERO : 0.0E+0                                                                                                                                                                                       
 # PT_OFF : 13500                                                                                                                                                                                       
 # YUNIT : "Volts"                                                                                                                                                                                      
 # YMULT : 31.25E-6                                                                                                                                                                                     
 # YOFF : 128.0E+0                                                                                                                                                                                      
 # YZERO : 0.0E+0                                                                                                                                                                                       
 # :WFMPRE:CH3:WFID : "Ch3, DC coupling, 200.0mVolts/div, 50.00ms/div, 15000 points, Pk Detect mode"                                                                                                    
 -16128.0                                                                                                                                                                                               
 -15360.0                                                                                                                                                                                               
 -16128.0                                                                                                                                                                                               
 -15360.0                                                                                                                                                                                               
 -16128.0                                                                                                                                                                                               
 -15360.0                                                                                                                                                                                               
 -16128.0                                                                                                                                                                                               
 -15360.0                                                                                                                                                                                               
 -16128.0                                                                                                                                                                                               
 -15360.0                                                                                                                                                                                               
 -16128.0                                                                                                                                                                                               
 -15360.0                                                                                                                                                                                               
 -16128.0                                                                                                                                                                                               
 -15360.0                                                                                                                                                                                               
 -16128.0                                                                                                                                                                                               
 -15360.0                                                                                                                                                                                               
 -16128.0                                                                                                                                                                                               
 -15360.0                                                                                                                                                                                               
 -16128.0                                                                                                                                                                                               
 -15360.0                                                                                                                                                                                               
 -16128.0                                                                                                                                                                                               
 -15360.0   
 ...
```
