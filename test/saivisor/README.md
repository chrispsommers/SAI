# saivisor-202111-d2c5824
This directory contains tools e.g. BPF saivisor probes which run in the following sonic repo versions. Herea re t

sonic-buildimage:
```
chris@chris-z4:~/chris-sonic1/sonic-buildimage$ git log
commit d2c582457e34c6e21643354a4b1d4002b4e71b03 (HEAD -> saivisor-202111, origin/saivisor-202111)
Author: Chris Sommers <chrispsommers@gmail.com>
Date:   Thu Feb 24 09:42:02 2022 -0800

    update sonic-sairedis submodule: added DTRACE probes for BULK QUAD Apis.

commit cc469368e9ffb559a306f63878c3df4dcad9acb9
Author: Chris Sommers <chrispsommers@gmail.com>
Date:   Fri Feb 18 19:29:48 2022 -0800

    Added debug tools (binutils) to docker base. Used buster backports for bpfcc tools.

commit b59bfad08df4caa036665e2bfe0dff00e5472ef2
Author: Chris Sommers <chrispsommers@gmail.com>
Date:   Mon Feb 14 18:24:31 2022 -0800

    Fix syncd USDT probe name (clear_stats_ret).

commit 51716995277a5469ee0ab2364851c34d5693bd0d
Author: Chris Sommers <chrispsommers@gmail.com>
Date:   Thu Feb 10 09:30:12 2022 -0800

    First commit of USDT tracing and tools. sonic-sairedis has USDT probes around SAI calls within VendosSai.cpp. SONiC slaves incloude sdt.h. Debian OS images contain bpfcc tools. Still need to add Linux headers to image in the build, currently has to be done manually on the box.

```

sonic-sairedis:
```
chris@chris-z4:~/chris-sonic1/sonic-buildimage/src/sonic-sairedis$ git log
commit 479f1170994dca5de9a6a737dc2768b582a21d6d (HEAD -> saivisor-202111, origin/saivisor-202111)
Author: Chris Sommers <chrispsommers@gmail.com>
Date:   Thu Feb 24 09:40:49 2022 -0800

    Added DTRACE probes around BULK QUAD apis. Verified via elf notes in syncd.

commit 17e2588d0de7000721678d96663603b4ad251e54
Author: Chris Sommers <chrispsommers@gmail.com>
Date:   Mon Feb 14 15:56:36 2022 -0800

    Better comments on probe macros. Fix clear stats "return" probe name (said "get").

commit f7d315b2eba318e3b12a3465b09960640137ceba
Author: Chris Sommers <chrispsommers@gmail.com>
Date:   Thu Feb 10 09:25:26 2022 -0800

    USDT macros in VendorSai.cpp including func args and ret values. Quad APIs + stats funcs traced.
```
# Design and architecture
See also [sai_api_hist7](README-sai_api_hist7.md) or highest-numbered version in this series of progams
# Building SONiC Image
# Installing SONiC Image
# Post-Install Fixup to SONiC Image In-Situ
# Misc. Hints and techniques
## Query USDT probes in the object file using `readelf`
This command prints out the ELF file "Notes" section.

For example, given the following two DTRACE probes:
```
    DTRACE_PROBE5(saivisor, sai_get_stats_fn, object_type, object_id, number_of_counters, counter_ids, counters);
    DTRACE_PROBE2(saivisor, sai_get_stats_ret, (int)object_type, status);

```
The corresponding entries in the ELF notes section are:
```
root@sonic:/home/chris# readelf -n /proc/2608/root/usr/bin/syncd
...
Displaying notes found in: .note.stapsdt
  Owner                Data size 	Description
  stapsdt              0x00000056	NT_STAPSDT (SystemTap probe descriptors)
    Provider: saivisor
    Name: sai_get_stats_fn
    Location: 0x000000000007d644, Base: 0x0000000000111e52, Semaphore: 0x0000000000000000
    Arguments: 4@%ebx 8@%rdi 4@%r15d 8@%r12 8@%r13
  stapsdt              0x00000043	NT_STAPSDT (SystemTap probe descriptors)
    Provider: saivisor
    Name: sai_get_stats_ret
    Location: 0x000000000007d652, Base: 0x0000000000111e52, Semaphore: 0x0000000000000000
    Arguments: -4@%ebx -4@%eax
...
```

"Provider" and "name" are the 1st and 2nd args in the DTRACE macro. "Name" is what is referenced when the probes are enabled/attached to BPF programs.

The arguments are interpreted as follows:
* The number before the `@` symbol is the size, e.g. `4` = 32-bits
* `-` indicates signed value e.g. signed `int`
* The label following the `@` sign is the location where the function args are passed, typically CPU registers, e.g. `ebx`
* Pointers are typically 8 bytes unsigned

## Querying enabled/running probes using `tplist-bpfcc`
This uses a canned bpfcc tool called `tplist` which discovers actual installed probes.
```
root@sonic:/home/chris# tplist-bpfcc -p `pidof syncd`
b'/proc/2608/root/usr/bin/syncd' b'saivisor':b'sai_get_stats_fn'
b'/proc/2608/root/usr/bin/syncd' b'saivisor':b'sai_get_stats_ret'
...
b'/proc/2608/root/usr/bin/syncd' b'saivisor':b'sai_get_stats_ext_fn'
b'/proc/2608/root/usr/bin/syncd' b'saivisor':b'sai_get_stats_ext_ret'
b'/proc/2608/root/usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.25' b'libstdcxx':b'catch'
b'/proc/2608/root/usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.25' b'libstdcxx':b'throw'
b'/proc/2608/root/usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.25' b'libstdcxx':b'rethrow'
```
Count the `saivisor` probes:
```
root@sonic:/home/chris# tplist-bpfcc -p `pidof syncd`|grep saivisor|wc
     82     164    5943
```
82 probes/2 = 41 unique functions probed - each one has a `_fn` entry probe and a `_ret` return probe (based on our usage in `syncd`, not on any fact of probes in general).
