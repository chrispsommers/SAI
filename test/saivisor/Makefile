all:protos deploy

protos:
	make -C saivisor_grpc/proto all

clean: clean_pycache
	make -C saivisor_grpc/proto clean

clean_pycache:
	-find . -name __pycache__ -exec rm -rf {} \;

deploy: clean_pycache tarball

APP = saivisor.py

tarball:
	tar czf saivisor.tgz $(APP) bpfmetrics grafana saibpf saiutils saivisor_grpc requirements.txt



