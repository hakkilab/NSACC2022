#!/bin/bash
git clone https://github.com/openssh/openssh-portable
cd openssh-portable
autoreconf
./configure --with-audit=debug CPPFLAGS=-O0
make ssh-keygen
mv ssh-keygen ..