domain_name='my.domain.ntu.edu.tw'
mysql_root_passowrd='mysql_root_password'
mysql_passowrd='mysql_password'
home='\/home\/ubuntu'

# test
echo "Change ip and cert and key"
vim traefik.yml

# domain and port
echo "Change domain name and port and sql password"
sed -i "s/my.domain.ntu.edu.tw/$domain_name/g" ../Nextcloud/nginx*
sed -i "s/my.domain.ntu.edu.tw/$domain_name/g" nextcloud_collabora.yml
sed -i "s/mysql_root_password/$mysql_root_password/g" nextcloud_db.yml
sed -i "s/mysql_passowrd/$mysql_password/g" nextcloud_db.yml
sed -i "s/\~/$home/g" *.yml
