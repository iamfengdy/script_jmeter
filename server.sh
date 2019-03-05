:<<!
@Author:fengdy
@Email:iamfengdy@126.com
@DateTime:五  3/ 1 17:17:44 2019
!
_IFS=$IFS
IFS=$";"
cmds="./clean.sh;./scp.sh;ls"
for cmd in $cmds
do 
    echo $cmd
    $cmd
done
IFS=$_IFS
