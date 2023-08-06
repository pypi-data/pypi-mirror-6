# set up the users database
#  create user with name provided by argument 1
#  create database for this user
#
# to be run as user 'postgres' with argument user
user=${1:?"Please specify user as first argument"}
psql <<EOF
create user ${user};
create database ${user} owner ${user};
EOF
