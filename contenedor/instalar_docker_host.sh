#!/usr/bin/env bash
# Ejecutar en la terminal del escritorio Ubuntu, no dentro del contenedor.
set -euo pipefail
source /etc/os-release
[[ "$ID" == ubuntu && "$VERSION_ID" == 26.04 ]] || {
  echo 'Este paso fue preparado para la VM Ubuntu 26.04 detectada.'; exit 1;
}
sudo apt-get update
sudo apt-get install -y docker.io acl
sudo systemctl enable --now docker
# Acceso de este usuario al daemon sin reiniciar la sesión del escritorio.
# La ACL puede perderse al reiniciar Docker; no se abre acceso a otros usuarios.
sudo setfacl -m "u:$(id -un):rw" /var/run/docker.sock
docker version
