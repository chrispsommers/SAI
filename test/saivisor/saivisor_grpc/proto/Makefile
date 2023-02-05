all: protos 

PB2_BUILD_DIR ?= $(shell pwd)/../pb2

PYTHON_PROTOC=python3 -m grpc_tools.protoc

# Full path names of all .proto files:
PROTO_SRC_PATHS = $(shell find . -name '*.proto')
# Just the file names w/o directory
PROTO_SRCS = $(notdir $(PROTO_SRC_PATHS))
# Just the directories; sorted to remove duplicates
PROTO_DIRS = $(sort $(dir $(PROTO_SRC_PATHS)))
# Directories containing protos with colons
VPATHS = $(addsuffix :,$(PROTO_DIRS))
# Protoc include paths = all the directories containing protobufs
# PROTO_INCL = $(addprefix -I,$(PROTO_DIRS)) -I.
PROTO_INCL = -I.

vpath %.proto $(VPATHS)

# PYTHON_PROTOC-generated python protobuf modules:
PROTO_PB2S = $(addprefix $(PB2_BUILD_DIR)/, $(PROTO_SRCS:.proto=_pb2.py) )

# This assumes every proto has an RPC; can also list specific 
# Protoc-generated Python grpc modules:
PROTO_GRPC_PB2S = $(addprefix $(PB2_BUILD_DIR)/, $(PROTO_SRCS:.proto=_pb2_grpc.py) )

# All compiled cc files
$(PB2_BUILD_DIR)/%_pb2.py: %.proto
	$(PYTHON_PROTOC) $(PROTO_INCL) --python_out=$(PB2_BUILD_DIR) $<

$(PB2_BUILD_DIR)/%_pb2_grpc.py: %.proto
	$(PYTHON_PROTOC) $(PROTO_INCL) --grpc_python_out=$(PB2_BUILD_DIR) $<

build_dirs:
	mkdir -p $(PB2_BUILD_DIR)

dump:
	@echo PROTO_SRC_PATHS=$(PROTO_SRC_PATHS)
	@echo PROTO_SRCS=$(PROTO_SRCS)
	@echo PROTO_DIRS=$(PROTO_DIRS)
	@echo PROTO_INCL=$(PROTO_INCL)
	@echo VPATHS=$(VPATHS)
	
protos: build_dirs dump $(PROTO_PB2S) $(PROTO_GRPC_PB2S)
	find $(PB2_BUILD_DIR) -type d -exec touch {}/__init__.py \;
	@echo "Built all protos under $(PB2_BUILD_DIR)"

clean:
	rm -rf $(PB2_BUILD_DIR)
