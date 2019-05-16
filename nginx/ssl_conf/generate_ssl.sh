#!/bin/bash
echo "Starting sctipt $0"

display_usage() {
  echo
  echo "Usage: $0"
  echo
  echo " -h, --help   Display usage instructions"
  echo " -t, --testing  Test mode"
  echo " -l, --letsencrypt  Use Let's encrypt/Use OpenSSL (default if not specified)"
  echo " -d, --domains  Domain names -d korek.com -d www.korek.com -d korek.net"
  echo
}


staging=0
letsencrypt=0
domains=""

staging_message() {
  echo "Test mode activated"
  staging=1
}

generate_message() {
  echo "Generate certificate"
  letsencrypt=1
}

domain_message() {
  echo "Add domain name"
}

raise_error() {
  local error_message="$@"
  echo "${error_message}" 1>&2;
}

while (( "$#" )); do
argument="$1"
    if [[ -z $argument ]] ; then
    raise_error "Expected argument to be present"
    display_usage
    else
    case $argument in
        -h|--help)
        display_usage
        break
        ;;
        -t|--testing)
        staging_message
        shift
        ;;
        -l|--letsencrypt)
        generate_message
        shift
        ;;
        -d|--domains)
        domains=$2" "$domains
        domain_message
        shift 2
        if [ ! $2  ]; then 
            break 
        fi
        ;;
        *)
        raise_error "Unknown argument: ${argument}"
        display_usage
        break
        ;;
    esac
    fi
done

dummy_ssl=1
if [ $letsencrypt ] && [ $letsencrypt -eq 1 ]; then 
    dummy_ssl=0 
fi

if [ -n "$domains" ]; then
    domains=($domains)
    echo "set" $domains
else
    domains=(korek.ddns.net)
fi

data_path="/data/certbot"

if [ $dummy_ssl -eq 1 ]; then
    echo "### Creating dummy certificate for $domains ..."
    path="/etc/letsencrypt/live/$domains"
    mkdir -p "$path"
    # Mark for the certificate
    mkdir -p "$data_path/conf/live/$domains"
    # Disable crontab for Let's encrypt renewal'
    crontab -l | grep -v 'Renew SSL' | crontab -
    # Generate dummy SSL
    openssl req -x509 -nodes -newkey rsa:1024 -days 365 \
        -keyout ${path}'/privkey.pem' \
        -out ${path}'/fullchain.pem' \
        -subj '/CN='$domains
fi


if [ $letsencrypt -eq 1 ]; then

    echo "### Deleting dummy certificate for $domains ..."
    rm -Rf /etc/letsencrypt/live/$domains && \
    rm -Rf /etc/letsencrypt/archive/$domains && \
    rm -Rf /etc/letsencrypt/renewal/$domains.conf
    echo

    echo "### Requesting Let's Encrypt certificate for $domains ..."
    #Join $domains to -d args
    domain_args=""
    for domain in "${domains[@]}"; do
      domain_args="$domain_args -d $domain"
    done
    echo "Domains:$domain_args"


    # Enable staging mode if needed
    if [ $staging != "0" ]; then staging_arg="--staging"; fi

    # Generate Let's encrypt SSL
    mkdir -p /var/www/certbot
    certbot certonly --webroot -w /var/www/certbot \
        $staging_arg \
        --register-unsafely-without-email \
        $domain_args \
        --agree-tos

    # Add Renewal each 12 hours
    crontab -l | grep -v 'Renew SSL' | crontab -
    crontab -l | { cat; echo "0 0,12 * * * /bin/bash -c \"echo 'Renew SSL certificate' && certbot renew && echo 'Restart Nginx' && nginx -s reload\""; } | crontab -
    service cron start
fi


echo "### Apply SSL settings to Nginx ..."

# Set Nginx for HTTPS Only
cp /etc/nginx/conf.d/app.conf /tmp/initial_app.conf
server_name=$(cat /tmp/initial_app.conf | grep server_name | head -1 | cut -d " " -f6 | cut -d ";" -f1)
sed 's/'"$server_name"'/'"$domains"'/g' /tmp/initial_app.conf > /tmp/app.conf
sed 's/#ssl_certificate/ssl_certificate/g' /tmp/app.conf > /tmp/initial_app.conf 
sed 's/#listen 443/listen 443/g' /tmp/initial_app.conf > /tmp/app.conf
sed 's/ listen 80;/ #listen 80;/g' /tmp/app.conf > /tmp/initial_app.conf
# Redirect all HTTP requets to HTTPS
sed 's/#!//g' /tmp/initial_app.conf > /tmp/app.conf

cat /tmp/app.conf > /etc/nginx/conf.d/app.conf

echo "### Reloading Nginx ..."
nginx -s reload