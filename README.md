nsxchecker
===

nsxchecker iterates ports on a logical network and tests connectivity from each.

    time ./nsxchecker.py  --controller <controller> --password '<password>' --network <lswitch uuid|neutron network uuid> [--quiet] [--full]

    22 ports on this network.
    ab:cd:ef:08:c1:57 -> ab:cd:ef:08:81:48: False
    ab:cd:ef:08:23:f8 -> ab:cd:ef:08:81:48: True
    ab:cd:ef:08:c2:f7 -> ab:cd:ef:08:81:48: True
    ab:cd:ef:08:63:18 -> ab:cd:ef:08:81:48: True
    ab:cd:ef:08:42:a5 -> ab:cd:ef:08:81:48: True
    ab:cd:ef:08:45:52 -> ab:cd:ef:08:81:48: True
    ab:cd:ef:08:59:3b -> ab:cd:ef:08:81:48: True
    ab:cd:ef:08:c2:cd -> ab:cd:ef:08:81:48: True
    ab:cd:ef:08:c2:c9 -> ab:cd:ef:08:81:48: True
    ab:cd:ef:08:0b:37 -> ab:cd:ef:08:81:48: True
    ab:cd:ef:08:03:8c -> ab:cd:ef:08:81:48: False
    ab:cd:ef:08:c3:05 -> ab:cd:ef:08:81:48: True
    ab:cd:ef:08:97:20 -> ab:cd:ef:08:81:48: True
    ab:cd:ef:08:bf:85 -> ab:cd:ef:08:81:48: True
    ab:cd:ef:08:a1:7a -> ab:cd:ef:08:81:48: True
    ab:cd:ef:08:c2:ee -> ab:cd:ef:08:81:48: False
    ab:cd:ef:08:b2:78 -> ab:cd:ef:08:81:48: True
    ab:cd:ef:08:89:1f -> ab:cd:ef:08:81:48: True
    ab:cd:ef:08:c0:65 -> ab:cd:ef:08:81:48: True
    ab:cd:ef:08:c2:c7 -> ab:cd:ef:08:81:48: True
    ab:cd:ef:08:0e:bb -> ab:cd:ef:08:81:48: True
    ----------------------------------------
    85 percent successful (network ID: <removed>)
    14 percent fail (network ID: <removed>)

    real    0m6.332s
    user    0m0.351s
    sys     0m0.142s
