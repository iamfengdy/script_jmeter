:<<!
@Author:fengdy
@Email:iamfengdy@126.com
@DateTime:五  3/ 1 17:17:44 2019
!
./clean.sh 
total=$1
minutes=$2
next_ms=0   #next minute:second
error_count=0
if [ ! $total ]
then
    total=1
fi
if [ ! $minutes ] || (($minutes < 1)) || (($minutes > 5));
then
    minutes=1
fi
if [ $total == 1 ]
then
    minutes=0
fi
function analyse(){
    message=$*
    message=${message##*summary =}
    result=${message%%Tidying *}
    time=${message##*Tidying up}
    time=${time%%end of ru*}
    error=${result##*Err:}
    error=${error%%(*}
    error=${error// /}
    if [ ! $error == 0 ]
    then
        let error_count++
    fi
    echo "Result: "$result
    echo "Time: "$time
}
function get_next_ms(){
    local i=$1
    #echo $i
    #echo $minutes
    #let next_i=$1+$minutes
    #next_i=$(($1 + $minutes))
    next_i=$[ 10#$i + minutes ]
    #echo '$1='$i '$next_i='$next_i
    result=$next_i
    if [ $next_i == "60" ]
    then
        result="00" 
    fi
    if [ ${#next_i} == 1 ]
    then
        result="0"$next_i
    fi
    next_ms=$result"00"
}
function run_period(){
    no=$1
    folder=$2
    echo ""
    echo "No: "$no" Path:"$folder
    mkdir $folder
    message=$("./start.sh")
    analyse $message
    mv ./result.txt $folder"/"
    mv ./html $folder"/"
}

echo ""
echo "================================="
echo "Total: "$total" Sleep: "$minutes
now_minute=`date "+%M"`
get_next_ms $now_minute
if [ $total -gt 1 ]
then
    echo "First run on: "$next_ms
fi
for ((i=1; i<=$total; i++))
do
    now_dh=`date "+%d%H"`
    now_ms=`date "+%M%S"`
    if [ $total -eq 1 ]
    then
        run_period $i $now_dh$now_ms
        continue
    fi
    goon=true
    while $goon
    do
        now_ms=`date "+%M%S"`
        #echo $now_ms "==" $next_ms
        if [ $now_ms == $next_ms ]
        then
            get_next_ms ${now_ms:0:2}
            run_period $i $now_dh$now_ms
            goon=false
        fi
    done
done
echo ""
echo "Error count: "$error_count
echo "================================="
