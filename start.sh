:<<!
@Author:fengdy
@Email:iamfengdy@126.com
@DateTime:五  3/ 1 17:17:44 2019
!
_IFS=$IFS
IFS=$";"
cmds="jmeter -n -t test-tcp.jmx -l ./result.txt -e -o ./html"
for cmd in $cmds
do 
    echo "#] "$cmd
    eval $cmd
done
IFS=$_IFS
