GPUFan
======

A module to control Nvidia Graphic Cards' fan in your python script.

## Why?

My deep learning rig contains 2 GTX 1080ti graphic cards with no liquid cooling. It takes only a few minutes for the GPUs to hit the thermal threshold of 86°C after I start a training process. Yet, it only uses fans at 50% rate.

There is an option to control fan speed manually using Nvidia Preferences GUI. But it annoys me run a desktop to control fans!

There are scripts around that use `nvidia-settings` to control fan right in the command line. Actually, I used them a lot and I am not satisfied. So I built mine.

## What is special about it?

It integrates with my python scripts. The immediate benefit is that it gives control back to the driver after the work is finished. So I don't hear the noise more than necessary!

It can be used as a standalone script with enough options to control GPUs indiviually.

# How to use it?

Import it and call the approperiate control function:

```
import gpufan

gpu_index = 0

# Fan at constant speed of 60%
gpufan.constant(gpu_index, 60)

# Use an aggressive control
gpufan.aggressive(gpu_index)

# Give control back to the driver manually (after execution is finished, this line is automatically called so you don't have to)
gpufan.driver()
```

## Caution

Use this module at your own risk. The author takes no responsibility.
