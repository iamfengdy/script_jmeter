:<<!
@Author:fengdy
@Email:iamfengdy@126.com
@DateTime:三  3/ 6 09:33:31 2019
!
jmx_files="10"
thread_nums="100"
timeout_nums="20"
time_sleep=1m
run_total=30
run_interval=1
run_count=10
cmds="jmeter -n -t _FILE_NAME.jmx -l result.txt -e -o html -JTHREAD_NUM=_THREAD_NUM -JTIMEOUT=_TIMEOUT000 -JSERVER_IP=47.110.151.58"
file_name="./"`date "+%Y%m%d%H%M%S"`".sh"
file_name="./temp.sh"

function create_file(){
    if [ ! -e $file_name ] 
    then
        touch $file_name
        chmod +x $file_name
    fi
    echo 'eval "'$*'"' > $file_name 
}

function clean_files(){
    if [ -e "./html" ]
    then
        rm -rf ./html
    fi
    if [ -e "./result.txt" ]
    then
        rm -rf ./result.txt
    fi
}

function clean(){
    clean_files
    if [ -e $file_name ]
    then
        rm -rf $file_name
    fi
}

function run_period(){
   for thread_num in $thread_nums
   do
       for timeout_num in $timeout_nums
       do
           for jmx_file in $jmx_files
           do
                clean_files
                cmd=${cmds//_FILE_NAME/$jmx_file}
                cmd=${cmd//_THREAD_NUM/$thread_num}
                cmd=${cmd//_TIMEOUT/$timeout_num}
                echo $cmd
                create_file $cmd
                ./period.sh $run_total $run_interval $file_name
                sleep 1m
            done
        done
    done
    clean    
}

jmx_files="60 30 10"
thread_nums="140 120 100"
timeout_nums="30 20"
run_period

