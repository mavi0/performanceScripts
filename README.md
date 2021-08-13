# performanceScripts
Scripts to monitor network performance

Example docker-compose conifg

```yaml

version: "3.3"

services:
  watchtower:
    container_name: watchtower
    image: containrrr/watchtower:latest
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    command: --interval 30 performancescripts gstreamerparser telegraf

  performancescripts:
    image: ghcr.io/mavi0/performancescripts:latest
    container_name: performancescripts
    networks:
      - monitor-services
      - default
    environment:
      - PUID=${PUID}
      - PGID=${PGID}
      - TZ=${TZ}
      - INTERVAL=${INTERVAL}
      - CLIENT_ID=${CLIENT_ID}
      - HOST_ID=${HOST_ID}
      - DURATION=${DURATION}
      - PROTOCOL=${PROTOCOL}
      - NUM_STREAMS=${NUM_STREAMS}
      - PORT=${PORT}
      - PORT_RANGE=${PORT_RANGE}
      - BLKSIZE=${BLKSIZE}
      - IPERF_RETRY=${IPERF_RETRY}
    volumes:
      - ${LOG_DIR}:/log
      - ${SHARE_DIR}:/share
    restart: unless-stopped

  gstreamerparser:
    image: mavi0/gstreamerparser:latest
    container_name: gstreamerparser
    networks:
      - monitor-services
      - default
    environment:
      - PUID=${PUID}
      - PGID=${PGID}
      - TZ=${TZ}
      - INTERVAL=${QOE_INTERVAL}
      - CLIENT_ID=${CLIENT_ID}
    volumes:
      - ${LOG_DIR}:/log
      - ${SHARE_DIR}:/share
    restart: unless-stopped
  
  telegraf:
    image: telegraf:1.14.4-alpine
    container_name: telegraf
    networks:
      - monitor-services
      - default
    environment:
      - PUID=${PUID}
      - PGID=${PGID}
      - TZ=${TZ}
      - HOST_PROC=/host/proc
      - INFLUX_USER=${INFLUX_USER}
      - INFLUX_DB=${INFLUX_DB}
      - INFLUX_URL=${INFLUX_URL}
      - INFLUX_SKIP_DATABASE_CREATION=${INFLUX_SKIP_DATABASE_CREATION}
      - INFLUX_PASSWORD=${INFLUX_PASSWORD}
      - TELEGRAF_CONF=${TELEGRAF_CONF}
      - BAUTH_USER=${BAUTH_USER}
      - BAUTH_PASSWORD=${BAUTH_PASSWORD}
      - CLIENT_ID=${CLIENT_ID}
      - INTERVAL=${INTERVAL}
      - QOE_INTERVAL=${QOE_INTERVAL}
      - TELEGRAF_INTERVAL=${TELEGRAF_INTERVAL}


    volumes:
      - ./.env:/etc/default/telegraf:ro
      - ${LOG_DIR}:/log
      - ${SHARE_DIR}:/share
      - ./telegraf.conf:/etc/telegraf/telegraf.conf:ro
      - /proc:/host/proc:ro
    restart: unless-stopped

  
networks:
  monitor-services:
    external: true
  default:
    driver: bridge
    
```
