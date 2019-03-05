:<<!
@Author:fengdy
@Email:iamfengdy@126.com
@DateTime:五  3/ 1 17:17:44 2019
!

_IFS=$IFS
IFS=$";"
cmds="rm -rf ./html ./result.txt;ls"
for cmd in $cmds
do 
    echo "#] "$cmd
    eval $cmd
done
IFS=$_IFS
