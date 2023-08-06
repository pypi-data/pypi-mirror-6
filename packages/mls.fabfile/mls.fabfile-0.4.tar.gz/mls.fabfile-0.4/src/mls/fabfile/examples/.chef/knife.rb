# Logging.
log_level                         :info
log_location                      STDOUT

# Chef server configuration.
chef_server_url                   "#{ENV['KNIFE_CHEF_SERVER']}"
client_key                        "#{ENV['KNIFE_CLIENT_KEY']}"
node_name                         "#{ENV['KNIFE_NODE_NAME']}"
validation_client_name            "#{ENV['KNIFE_VALIDATION_CLIENT_NAME']}"
validation_key                    "#{ENV['KNIFE_VALIDATION_CLIENT_KEY']}"
encrypted_data_bag_secret         "#{ENV['ENCRYPTED_DATA_BAG_SECRET_FILE']}"

# Rackspace API configuration.
knife[:rackspace_api_key]       = "#{ENV['RACKSPACE_API_KEY']}"
knife[:rackspace_api_username]  = "#{ENV['RACKSPACE_USERNAME']}"
knife[:rackspace_endpoint]      = "#{ENV['RACKSPACE_ENDPOINT']}"
knife[:rackspace_version]       = "#{ENV['RACKSPACE_VERSION']}"
