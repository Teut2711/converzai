FROM docker.elastic.co/logstash/logstash:8.11.0

# Copy custom configuration
COPY logstash.yml /usr/share/logstash/config/logstash.yml
COPY config/ /usr/share/logstash/pipeline/

# Create data directory
RUN mkdir -p /usr/share/logstash/data

# Expose ports
EXPOSE 5044 9600
