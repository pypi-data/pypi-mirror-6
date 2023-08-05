#! /bin/sh
# PLEASE sync 42-jobs:jobs/apps/core/scripts/trac.* and 42-kavyarnya:bin/trac.*
DESC="Tracs manage script"

HELP="error=Usage: $SCRIPTNAME {copy trac1 trac2|adduser trac username [password]|tracadduser trac username|userslist}"

cd $(dirname $0)

TRAC_URL="$1"
USER="$2"
TRACS_DIR="$3"
HTPASSWD_FILE="$4"
CHGRP="$5"

SSH="ssh -oBatchMode=yes"

for VARNAME in "TRAC_URL" "HTPASSWD_FILE" "TRACS_DIR" "USER" "CHGRP" ; do
    if [ -z ${!VARNAME} ] ; then
	echo "error=${VARNAME} not defined!"
	exit 9
    fi
done

if ! which apg >/dev/null; then
    echo "error=apg not installed?"
    exit 10
fi

create_password() {
    local PASSW=`apg -m 10 -n 1 -M NnCc`
    echo $PASSW
}

copy_trac() {
    command="test -d \"$TRACS_DIR/$2\" && exit 5"
    command="${command} ; cp -r \"$TRACS_DIR/$1\" \"$TRACS_DIR/$2\""
    command="${command} ; chgrp -R \"$CHGRP\" \"$TRACS_DIR/$2\""
    command="${command} ; chmod -R g+rwX \"$TRACS_DIR/$2\""
    echo -e $command | ${SSH} $USER@$TRAC_URL 2>/dev/null
}

create_user() {
    command="test -f $HTPASSWD_FILE || (touch $HTPASSWD_FILE ; chgrp -R \"$CHGRP\" \"$TRACS_DIR/$2\" ; chmod -R g+rwX \"$TRACS_DIR/$2\")"
    command="${command} ; grep -qw $2 $HTPASSWD_FILE && exit 13"
    command="${command} ; htpasswd -b $HTPASSWD_FILE $2 $3 || exit 12"
    echo -e $command | ${SSH} $USER@$TRAC_URL 2>/dev/null
}

trac_add_user() {
    command="test -f $HTPASSWD_FILE || (touch $HTPASSWD_FILE ; chgrp -R \"$CHGRP\" \"$TRACS_DIR/$2\" ; chmod -R g+rwX \"$TRACS_DIR/$2\")"
    echo -e $command | ${SSH} $USER@$TRAC_URL 2>/dev/null
}

users_list() {
    command="echo \">>>\""
    command="${command} ; test -f $HTPASSWD_FILE || exit 15"
    command="${command} ; cat $HTPASSWD_FILE | cut -d ':' -f 1"
    command="${command} ; echo \"<<<\""
    echo -e $command | ${SSH} $USER@$TRAC_URL 2>/dev/null
}

case "$6" in
    copy)
        if [ $7 ] && [ $8 ]; then
            copy_trac $7 $8
        else
            echo ${HELP}
            exit 3
        fi
    ;;
    adduser)
        if [ $9 ]; then
            password=$9
        else
            password=$(create_password)
            echo "password=${password} "
        fi
        if [ $7 ] && [ $8 ] && [ $password ]; then
            create_user $7 $8 $password
        else
            echo ${HELP}
            exit 3
        fi

    ;;
    tracadduser)
        if [ $7 ] && [ $8 ]; then
            trac_add_user $7 $8
        else
            echo ${HELP}
            exit 3
        fi
    ;;
    userslist)
        users_list
    ;;
    *)
        echo ${HELP}
        exit 3
    ;;
esac
exit $?
