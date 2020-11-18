# Generating new protobuf messages

1) modify reservation.proto
2) run notectl system protoco reservation.proto
3) copy resulting files to plugins/reservation_client/noteworthy/reservation_client/proto
4) add method to reservation_client

#TODO automate this