#!/bin/sh

# We're going to need the following environment variables as input
#
# - KAFKA_BOOTSTRAP_SERVERS - the URL of the Kafka service we're using
# - KAFKA_CA_CERT - the contents of the ca.pem file
# - KAFKA_ACCESS_CERT - the contents of the service.cert file
# - KAFKA_ACCESS_KEY - the contents of the service.key file
# - SCHEMA_REGISTRY_HOST - the host for the Karapace schema - this must
#   be without `https://`, it's just the host name
# - SCHEMA_REGISTRY_PORT - the port for the Karapace schema
# - SCHEMA_REGISTRY_PASSWORD - the password for the schema registry
#
# We also need the names of the input and output topics
# - INPUT_TOPIC - the input topic name
# - OUTPUT_TOPIC - the output topic name
#
# We also need the details of the anomaly we're trying to detect
# - FIELD_NAME is the name of the field in the Avro message
# - MIN_BOUND is the integer value that is the lowest "OK" value
# - MAX_BOUND is the integer value that is the highest "OK" value
#
export SCHEMA_REGISTRY_URL=https://${SCHEMA_REGISTRY_HOST}:${SCHEMA_REGISTRY_PORT}
# If you give a value for SCHEMA_REGISTRY_USERNAME we'll use it, otherwise
# we'll use the default value, which is "avnadmin"
export SCHEMA_REGISTRY_USERNAME=${SCHEMA_REGISTRY_USERNAME:-"avnadmin"}
#
# You can also request exactly once semantics by specifying true.
# The case of the value does not matter. The default is false.
export EXACTLY_ONCE=${EXACTLY_ONCE:-"false"}

export APP_NAME="AnomalyDetectorApp"

echo "APP_NAME is $APP_NAME"
echo "Detecting $FIELD_NAME outwith $MIN_BOUND .. $MAX_BOUND"

export JAVA_HOME=/usr/lib/jvm/custom-jre
export PATH=$JAVA_HOME/bin:$PATH

. ./setup_auth.sh

echo "RUN THE PROGRAM"
exec java \
    -cp '$JAVA_HOME/lib/*' \
    -DKAFKA_BOOTSTRAP_SERVERS="$KAFKA_BOOTSTRAP_SERVERS"                   \
    -DKAFKA_CA_CERT="$KAFKA_CA_CERT"		       \
    -DKAFKA_ACCESS_CERT="$KAFKA_ACCESS_CERT"           \
    -DKAFKA_ACCESS_KEY="$KAFKA_ACCESS_KEY"             \
    -DSCHEMA_REGISTRY_URL="$SCHEMA_REGISTRY_URL"               \
    -DSCHEMA_REGISTRY_USERNAME="$SCHEMA_REGISTRY_USERNAME"     \
    -DSCHEMA_REGISTRY_PASSWORD="$SCHEMA_REGISTRY_PASSWORD"     \
    -DINPUT_TOPIC="$INPUT_TOPIC"                               \
    -DOUTPUT_TOPIC="$OUTPUT_TOPIC"                             \
    -DFIELD_NAME="$FIELD_NAME"				       \
    -DMIN_BOUND="$MIN_BOUND"				       \
    -DMAX_BOUND="$MAX_BOUND"				       \
    -DEXACTLY_ONCE="$EXACTLY_ONCE"                             \
    -jar ./${APP_NAME}-uber.jar \
    com.example.${APP_NAME} "$@"
