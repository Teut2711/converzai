FROM docker.elastic.co/elasticsearch/elasticsearch:8.11.0

# Copy custom configuration files
COPY elasticsearch.yml /usr/share/elasticsearch/config/elasticsearch.yml

# Create data directory
RUN mkdir -p /usr/share/elasticsearch/data

# Expose ports
EXPOSE 9200 9300
