#ifndef VA_PROFILES_H
#define VA_PROFILES_H

#include <va/va.h>

// Function to get profile names
const char *get_profile_name(VAProfile profile)
{
    switch (profile)
    {
    case VAProfileMPEG2Simple:
        return "MPEG-2 Simple";
    case VAProfileMPEG2Main:
        return "MPEG-2 Main";
    case VAProfileMPEG4Simple:
        return "MPEG-4 Simple";
    case VAProfileMPEG4AdvancedSimple:
        return "MPEG-4 Advanced Simple";
    case VAProfileMPEG4Main:
        return "MPEG-4 Main";
#ifdef VAProfileH264Baseline
    case VAProfileH264Baseline:
        return "H.264 Baseline (Deprecated)";
#endif
    case VAProfileH264Main:
        return "H.264 Main";
    case VAProfileH264High:
        return "H.264 High";
    case VAProfileVC1Simple:
        return "VC-1 Simple";
    case VAProfileVC1Main:
        return "VC-1 Main";
    case VAProfileVC1Advanced:
        return "VC-1 Advanced";
    case VAProfileH263Baseline:
        return "H.263 Baseline";
    case VAProfileJPEGBaseline:
        return "JPEG Baseline";
    case VAProfileH264ConstrainedBaseline:
        return "H.264 Constrained Baseline";
    case VAProfileVP8Version0_3:
        return "VP8";
    case VAProfileH264MultiviewHigh:
        return "H.264 Multiview High";
    case VAProfileH264StereoHigh:
        return "H.264 Stereo High";
    case VAProfileHEVCMain:
        return "HEVC Main";
    case VAProfileHEVCMain10:
        return "HEVC Main 10-bit";
    case VAProfileVP9Profile0:
        return "VP9 Profile 0";
    case VAProfileVP9Profile1:
        return "VP9 Profile 1";
    case VAProfileVP9Profile2:
        return "VP9 Profile 2";
    case VAProfileVP9Profile3:
        return "VP9 Profile 3";
    case VAProfileHEVCMain12:
        return "HEVC Main 12-bit";
    case VAProfileAV1Profile0:
        return "AV1 Profile 0";
    case VAProfileAV1Profile1:
        return "AV1 Profile 1";
    case VAProfileNone:
        return "Video Processing (Post-Processing)";
    case 5:
        return "H.264 Extended (Possibly Deprecated)";
    default:
        return "Unknown Profile";
    }
}

// Function to get entrypoint names
const char *get_entrypoint_name(VAEntrypoint entrypoint)
{
    switch (entrypoint)
    {
    case VAEntrypointVLD:
        return "Decoding (VLD)";
    case VAEntrypointEncSlice:
        return "Encoding (Slice)";
    case VAEntrypointVideoProc:
        return "Video Processing";
    default:
        return "Unknown Entrypoint";
    }
}

#endif // VA_PROFILES_H
