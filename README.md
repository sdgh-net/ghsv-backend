# ghsv-backend

监督系统的后端，基于 Flask。

## 依赖

### pymssql

Linux 系统上使用 pymssql 需要手动编译安装依赖 [freetds](ftp://ftp.freetds.org/pub/freetds/stable/freetds-1.3.13.tar.gz)

### nginx

nginx 参考配置文件位于 assets/nginx.conf

Linux 上的 nginx 需要注意以下权限问题与证书安装命令：

```
chcon system_u:object_r:httpd_config_t:s0 /root/sv/cert/*
/usr/sbin/setsebool httpd_can_network_connect=1

acme.sh --install-cert -d sv.sdgh.eu.org \
--key-file       /root/sv/cert/key.pem  \
--fullchain-file /root/sv/cert/cert.pem \
--reloadcmd     "service nginx force-reload"
```

### Python

本项目用到了 Python 3.10 的[新类型标注特性](https://docs.python.org/zh-cn/3.10/whatsnew/3.10.html#:~:text=PEP%20604%EF%BC%8C-,%E5%85%81%E8%AE%B8%20X%20%7C%20Y%20%E5%BD%A2%E5%BC%8F%E7%9A%84%E8%81%94%E5%90%88%E7%B1%BB%E5%9E%8B%E5%86%99%E6%B3%95,-PEP%20613%EF%BC%8C%E6%98%BE)，为了提供更好的 Python 版本管理，建议使用 [pyenv](https://github.com/pyenv/pyenv) 与 [pyenv/pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)，参考资料：[pyenv 和 pyenv-virtualenv 的安装、配置和使用 - 简书 (jianshu.com)](https://www.jianshu.com/p/c47c225e4bb5)

```shell
pip3 install -r requirements.txt
# 或者这个，适用于无法使用HTTPS的
sh ./install_req.sh
```

## 运行

```shell
python3 main.py
```

## 配置

在搭建了 nginx 的情况下，CORS、Cookies与HTTPS证书等问题均无需后端过多配置。

## 使用

虽然本项目部分页面有着内嵌的 Web 页面（如：`/user/login`），可以通过此类页面检查功能可用性，但更建议的使用方法是配合[前端](https://github.com/sdgh-net/ghsv-frontend)进行使用
