# bay - Refer to your drive bays using sensible names

I wrote this tool because I have a hard time remembering which drive bays in my NAS have get which name under `/dev/disk/by-path` and additionally getting confused because I actually want to use the stable names under `/dev/disk/by-id` when referring to the disks in the drive bays. As a result of that I have accidentallied the wrong disk a few times, clobbering the boot partition on my boot disk and offlining the wrong disk from my ZFS pool. So I wrote this tool.


## Tutorial

The tool reads a config file from an OS-dependent path with a specification of the drive bays you have and the stable names you want to use. It will print the path of the file when you run it without it:

```
$ bay
error: Config file `/root/.config/bay/bay.toml' not found.
```

For these examples, I'm using the following config file. This config file is also located under `examples/bay.toml`, which some added explanations:

```toml
[bays]
left-1 = "pci-0000:00:1f.2-ata-6"
left-2 = "pci-0000:00:1f.2-ata-5"
left-3 = "pci-0000:00:1f.2-ata-4"
left-4 = "pci-0000:00:1f.2-ata-3"

right-1 = "pci-0000:01:00.0-ata-1"
right-2 = "pci-0000:01:00.0-ata-2"
right-3 = "pci-0000:01:00.0-ata-3"
right-4 = "pci-0000:01:00.0-ata-4"

esata-1 = "pci-0000:00:1f.2-ata-1"
esata-2 = "pci-0000:00:1f.2-ata-2"

usb-front = "pci-0000:00:1a.7-usb-0:1:1.0-scsi-0:0:0:0"

[bay."*"]
stable_patterns = ["ata-*", "wwn-0x*"]

# Different patterns can be configured for different sets of drive bays.
[bay."usb-*"]
stable_patterns = ["usb-*"]
```

At the top is a list of drive bays with names I have given to them. My NAS has eight drive bays that I've split into two groups, `left-1` to `left-4` and `right-1` to `right-4`. Additionally, I have given a name to the two eSATA ports on the back and a USB port on the front. As you can see, order that the drive bays appear on the two SATA buses don't make any sense at all.

A good way to build this list is to simply let `watch ls -tl /dev/disk/by-path` run in a separate, then put in one disk into a bay and see which names appear at the top of the output. Then, put a disk into the next bay and so on.

Next you have to configure, which names you want to use to refer to the disk. Sometimes it's nice to use names that don't change, even if the disk is put into another drive bay or moved to another machine. The names under `/dev/disk/by-id` do exactly that. These names are for example built from the model and serial number of the disk, which are also printed on its label. This is why the file name patterns in `bay.<pattern>.stable_patterns` are relative to that directory.

You can use the key `stable_patterns` in the section `[bay."*"]` to declare which stable names to use for all disk. If you add additional sections where the `*` is replaced by a pattern that matches some of the drive bay names, you can override the `stable_patterns` key for those bays. The last matching section wins.

If instead you want to use some other names, e.g. the ones directly under `/dev`, you can use a pattern that starts with a `/` in that list, e.g. `stable_patterns = ['/dev/*']`.

I have chose to use names that start with `ata-`, which contain the model and serial number, as well as the [WWN](https://en.wikipedia.org/wiki/World_Wide_Name), which most disks also have on their label. But for the USB port, I found that those names work better and contain the name that the devices is providing in its USB descriptor.

Now that you have given names to your drive bays and chosen which names to use to refer to the disks, you can start using the drive bay names. When using `bay` on the command line directly, it will simply print the stable names it has found for all disk in all named drive bays:

```
$ ../.local/bin/bay left-1 left-2
/dev/disk/by-id/ata-WDC_WD40EFRX-68WT0N0_WD-WCC4E0HJ5349
/dev/disk/by-id/ata-WDC_WD30EFRX-68EUZN0_WD-WMC4N2157296
```

If a drive bay doesn't contain a disk, it is simply omitted:

```
$ ../.local/bin/bay left-3 left-4
/dev/disk/by-id/ata-ST3000DM001-1CH166_W1F2E8MC
```

You can use patterns to match multiple drive bays by their name. Use `-t` to see which disk corresponds to which drive bay. Then it will also print a line for bays that don't have a disk in them:

```
$ ../.local/bin/bay -t left-\*
left-1: /dev/disk/by-id/ata-WDC_WD40EFRX-68WT0N0_WD-WCC4E0HJ5349 /dev/disk/by-id/wwn-0x50014ee20c0165a9
left-2: /dev/disk/by-id/ata-WDC_WD30EFRX-68EUZN0_WD-WMC4N2157296 /dev/disk/by-id/wwn-0x50014ee659963cd4
left-3: (no device present)
left-4: /dev/disk/by-id/ata-ST3000DM001-1CH166_W1F2E8MC /dev/disk/by-id/wwn-0x5000c5005e5c437f
```

`-t` leads to all matched stable names to be printed, not just the first one (which are the `ata-*` names in my case). Use `-b` to get slightly shorter lines or use `-d` to see the path of the actual device node instead:

```
$ ../.local/bin/bay -tb left-\*
left-1: ata-WDC_WD40EFRX-68WT0N0_WD-WCC4E0HJ5349 wwn-0x50014ee20c0165a9
left-2: ata-WDC_WD30EFRX-68EUZN0_WD-WMC4N2157296 wwn-0x50014ee659963cd4
left-3: (no device present)
left-4: ata-ST3000DM001-1CH166_W1F2E8MC wwn-0x5000c5005e5c437f
$ ../.local/bin/bay -td left-\*
left-1: /dev/sdh
left-2: /dev/sdg
left-3: (no device present)
left-4: /dev/sdj
```

Now the interesting part is using `bay` to pass these names to other commands, e.g.:

```
$ sgdisk -p `../.local/bin/bay left-4`
Disk /dev/disk/by-id/ata-ST3000DM001-1CH166_W1F2E8MC: 5860533168 sectors, 2.7 TiB
[...]

Number  Start (sector)    End (sector)  Size       Code  Name
   1            2048      5860515839   2.7 TiB     BF01  zfs-00767f3c3e8a14f5
   9      5860515840      5860532223   8.0 MiB     BF07  
```

Or to create a ZPool with the four other disk in my NAS:

```
zpool create test raidz2 `../.local/bin/bay right-\*`
```

See `--help` for some additional switches.


## Development Setup

```
make venv
```
