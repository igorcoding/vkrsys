# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.box = "ubuntu/trusty64"

  config.vm.synced_folder "./", "/home/vagrant/vkrsys-dev"

  config.vm.network "forwarded_port", guest: 80, host: 8888

  config.vm.provision "shell",
    privileged: false,
    path: "production/deploy.sh"

  config.vm.provider "virtualbox" do |v|
    v.memory = 1600
    v.cpus = 4
    v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    v.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
  end

end
