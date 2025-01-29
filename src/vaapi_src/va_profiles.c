#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <va/va.h>
#include <va/va_drm.h>
#include <fcntl.h>
#include <unistd.h>
#include "va_profiles.h"

#define MAX_PROFILES 32
#define MAX_ENTRYPOINTS 10

// Function prototypes
int initialize_vaapi(const char *device, VADisplay *va_dpy, int *major, int *minor, const char **vendor);
void list_profiles(VADisplay va_dpy, FILE *json_file, int json_enabled, int is_nvidia, int is_intel);
int detect_gpu_vendor(const char *vendor);
void print_usage(const char *program_name);

int main(int argc, char **argv)
{
    if (argc < 2)
    {
        print_usage(argv[0]);
        return 1;
    }

    // JSON output handling
    int json_enabled = 0;
    const char *json_filename = NULL;
    if (argc == 4 && strcmp(argv[2], "--json") == 0)
    {
        json_enabled = 1;
        json_filename = argv[3];
    }

    VADisplay va_dpy;
    int major, minor;
    const char *vendor;

    if (initialize_vaapi(argv[1], &va_dpy, &major, &minor, &vendor) != 0)
        return 1;

    // Detect GPU type
    int gpu_type = detect_gpu_vendor(vendor);
    int is_nvidia = (gpu_type == 1);
    int is_intel = (gpu_type == 2);

    FILE *json_file = NULL;
    if (json_enabled)
    {
        json_file = fopen(json_filename, "w");
        if (!json_file)
        {
            perror("Failed to open JSON output file");
            vaTerminate(va_dpy);
            return 1;
        }
        fprintf(json_file, "{\n  \"VAAPI Version\": \"%d.%d\",\n  \"Driver Version\": \"%s\",\n  \"Profiles\": [\n",
                major, minor, vendor ? vendor : "Unknown");
    }

    list_profiles(va_dpy, json_file, json_enabled, is_nvidia, is_intel);

    if (json_enabled)
    {
        fprintf(json_file, "\n  ]\n}\n");
        fclose(json_file);
        printf("\n📄 JSON output saved to %s\n", json_filename);
    }

    vaTerminate(va_dpy);
    return 0;
}

// Function to print program usage
void print_usage(const char *program_name)
{
    fprintf(stderr, "Usage: %s <VAAPI device> [--json <output.json>]\n", program_name);
}

// Function to initialize VAAPI and retrieve driver info
int initialize_vaapi(const char *device, VADisplay *va_dpy, int *major, int *minor, const char **vendor)
{
    int fd = open(device, O_RDWR);
    if (fd < 0)
    {
        perror("Failed to open VAAPI device");
        return 1;
    }

    *va_dpy = vaGetDisplayDRM(fd);
    if (!*va_dpy)
    {
        fprintf(stderr, "Failed to get VAAPI display\n");
        close(fd);
        return 1;
    }

    if (vaInitialize(*va_dpy, major, minor) != VA_STATUS_SUCCESS)
    {
        fprintf(stderr, "Failed to initialize VAAPI\n");
        close(fd);
        return 1;
    }

    *vendor = vaQueryVendorString(*va_dpy);
    printf("VA-API Version: %d.%d\n", *major, *minor);
    printf("Driver Version: %s\n\n", *vendor ? *vendor : "Unknown");

    return 0;
}

// Function to detect GPU vendor (Intel/NVIDIA)
int detect_gpu_vendor(const char *vendor)
{
    if (vendor)
    {
        if (strstr(vendor, "NVIDIA") || strstr(vendor, "NVDEC"))
        {
            printf("⚠️  WARNING: Detected NVIDIA GPU. VAAPI only supports decoding on NVIDIA.\n");
            printf("⚠️  Use FFmpeg with NVENC for encoding:\n");
            printf("    ffmpeg -hwaccel cuda -i input.mp4 -c:v h264_nvenc -preset fast output.mp4\n\n");
            return 1;
        }
        if (strstr(vendor, "Intel") || strstr(vendor, "iHD"))
        {
            printf("✅ Detected Intel GPU (Quick Sync Video Supported).\n");
            printf("ℹ️  Use FFmpeg with QSV for best performance:\n");
            printf("    ffmpeg -hwaccel qsv -i input.mp4 -c:v h264_qsv -preset fast output.mp4\n\n");
            return 2;
        }
    }
    return 0;
}

// Function to list VAAPI profiles and entrypoints
void list_profiles(VADisplay va_dpy, FILE *json_file, int json_enabled, int is_nvidia, int is_intel)
{
    VAProfile profiles[MAX_PROFILES] = {VAProfileNone};
    int num_profiles = 0;

    if (vaQueryConfigProfiles(va_dpy, profiles, &num_profiles) != VA_STATUS_SUCCESS || num_profiles <= 0)
    {
        fprintf(stderr, "Failed to query VAAPI profiles or no profiles available\n");
        return;
    }

    int first_profile = 1;

    printf("VAAPI Supported Profiles and Entrypoints:\n");

    for (int i = 0; i < num_profiles && i < MAX_PROFILES; i++)
    {
        if (profiles[i] == VAProfileNone)
            continue;

        if (json_enabled)
        {
            if (!first_profile)
            {
                fprintf(json_file, ",\n");
            }
            first_profile = 0;
        }

        printf("  - %s (Profile ID: %d)\n", get_profile_name(profiles[i]), profiles[i]);

        if (json_enabled)
        {
            fprintf(json_file, "    { \"profile\": \"%s\", \"id\": %d, \"entrypoints\": [",
                    get_profile_name(profiles[i]), profiles[i]);
        }

        VAEntrypoint entrypoints[MAX_ENTRYPOINTS] = {0};
        int num_entrypoints = 0;
        int can_transcode = 0;

        if (vaQueryConfigEntrypoints(va_dpy, profiles[i], entrypoints, &num_entrypoints) == VA_STATUS_SUCCESS)
        {
            int first_entry = 1;
            for (int j = 0; j < num_entrypoints && j < MAX_ENTRYPOINTS; j++)
            {
                if (!first_entry && json_enabled)
                {
                    fprintf(json_file, ", ");
                }
                first_entry = 0;

                printf("      -> %s\n", get_entrypoint_name(entrypoints[j]));

                if (json_enabled)
                {
                    fprintf(json_file, "\"%s\"", get_entrypoint_name(entrypoints[j]));
                }

                // Fix: Correctly detect and print EncSliceLP for Intel GPUs
                if (entrypoints[j] == VAEntrypointVLD || entrypoints[j] == VAEntrypointEncSlice || entrypoints[j] == VAEntrypointEncSliceLP)
                    can_transcode++;
            }
        }

        if (json_enabled)
        {
            fprintf(json_file, "] }");
        }

        if (can_transcode >= 2)
        {
            printf(COLOR_GREEN "      ✅ TRANSCODING SUPPORTED\n" COLOR_RESET);
        }
        else
        {
            printf(COLOR_RED "      ❌ NO TRANSCODING\n" COLOR_RESET);
        }
    }
}
