:<<!
@Author:fengdy
@Email:iamfengdy@126.com
@DateTime:五  3/ 1 17:17:44 2019
!
cmd=$*
if [ ! $cmd ]
then
    cmd="jmeter -n -t test-tcp.jmx -l ./result.txt -e -o ./html"
fi
echo "#] "$cmd
eval $cmd
