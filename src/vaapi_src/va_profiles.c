#include <stdio.h>
#include <va/va.h>
#include <va/va_drm.h>
#include <fcntl.h>
#include <unistd.h>
#include "va_profiles.h"

#define MAX_PROFILES 32
#define MAX_ENTRYPOINTS 10

int main(int argc, char **argv)
{
    if (argc < 2)
    {
        printf("Usage: %s <VAAPI device path>\n", argv[0]);
        return 1;
    }

    int fd = open(argv[1], O_RDWR);
    if (fd < 0)
    {
        perror("Failed to open VAAPI device");
        return 1;
    }

    VADisplay va_dpy = vaGetDisplayDRM(fd);
    if (!va_dpy)
    {
        fprintf(stderr, "Failed to get VAAPI display\n");
        close(fd);
        return 1;
    }

    int major, minor;
    const char *vendor;
    if (vaInitialize(va_dpy, &major, &minor) != VA_STATUS_SUCCESS)
    {
        fprintf(stderr, "Failed to initialize VAAPI\n");
        close(fd);
        return 1;
    }

    vendor = vaQueryVendorString(va_dpy);
    printf("VA-API Version: %d.%d\n", major, minor);
    printf("Driver Version: %s\n\n", vendor ? vendor : "Unknown");

    VAProfile profiles[MAX_PROFILES] = {VAProfileNone};
    int num_profiles = 0;
    if (vaQueryConfigProfiles(va_dpy, profiles, &num_profiles) != VA_STATUS_SUCCESS || num_profiles <= 0)
    {
        fprintf(stderr, "Failed to query VAAPI profiles or no profiles available\n");
        vaTerminate(va_dpy);
        close(fd);
        return 1;
    }

    printf("VAAPI Supported Profiles and Entrypoints:\n");
    for (int i = 0; i < num_profiles && i < MAX_PROFILES; i++)
    {
        if (profiles[i] == VAProfileNone)
            continue;

        printf("  - %s (Profile ID: %d)\n", get_profile_name(profiles[i]), profiles[i]);

        // Query entrypoints for this profile
        VAEntrypoint entrypoints[MAX_ENTRYPOINTS] = {0};
        int num_entrypoints = 0;
        if (vaQueryConfigEntrypoints(va_dpy, profiles[i], entrypoints, &num_entrypoints) == VA_STATUS_SUCCESS)
        {
            int can_transcode = 0;
            for (int j = 0; j < num_entrypoints; j++)
            {
                printf("      -> %s\n", get_entrypoint_name(entrypoints[j]));
                if (entrypoints[j] == VAEntrypointVLD || entrypoints[j] == VAEntrypointEncSlice)
                {
                    can_transcode++;
                }
            }
            if (can_transcode >= 2)
            {
                printf("      ✅ TRANSCODING SUPPORTED\n");
            }
        }
    }

    vaTerminate(va_dpy);
    close(fd);
    return 0;
}
