package com.fbz.performancetest.util;

import java.awt.desktop.ScreenSleepEvent;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;

public class FpsMonitor extends Monitor {

    private final Device device;

    private final String packageName;
    private final ProcessUtil processUtil = new ProcessUtil();
    private String pid;
    private ArrayList<Map<String, String>> cpuResult = new ArrayList<>();

    private boolean isRun = false;


    public FpsMonitor(Device device, String packageName) {
        this.device = device;
        this.packageName = packageName;
    }

    public String getFps() {
        String SurfaceFlingers = processUtil.getBack(device.adbShell("dumpsys SurfaceFlinger --list"), this.device.pcId);
        String [] surfaceViews = SurfaceFlingers.strip().split(System.lineSeparator());
        String surfaceView = null;
        for(String surface : surfaceViews){
            if(!surface.contains("SurfaceView")){
                continue;
            }
            if(surface.contains("Background for")){
                continue;
            }
            if(!surface.contains(packageName)){
                continue;
            }
            if(surfaceView == null || surface.contains("BLAST")){
                surfaceView = surface;
            }

        }
        System.out.println("获取到的surface_view:" + surfaceView);
        String surfaceTimeAll = processUtil.getBack(device.adbShell(String.format("dumpsys SurfaceFlinger --latency '%s' ", surfaceView)), this.device.pcId);
        System.out.println(surfaceTimeAll);
        String [] surfaceTimeAllList = surfaceTimeAll.split(System.lineSeparator());
        List res = this._GetSurfaceFlingerFrameData(surfaceTimeAllList);
        System.out.println("fps timestamp :" + res);
        return "";
    }


    public List _GetSurfaceFlingerFrameData(String [] results){
//        """Returns collected SurfaceFlinger frame timing data.
//
//       Returns:
//         A tuple containing:
//         - The display's nominal refresh period in seconds.
//         - A list of timestamps signifying frame presentation times in seconds.
//         The return value may be (None, None) if there was no data collected (for
//         example, if the app was closed before the collector thread has finished).
//       """
//        # adb shell dumpsys SurfaceFlinger --latency <window name>
//        # printsr information about the last 128 frames displayed in
//        # that window.
//        # The data returned looks like this:
//        # 16954612
//        # 7657467895508   7657482691352   765749349975
//        # 7657484466553   7657499645964   7657511077881
//        # 7657500793457   7657516600576   7657527404785
//        # (...)
//        #z
//        # The first line is the refresh period (here 16.95 ms), it is followed
//        # by 128 lines w/ 3 timestamps in nanosecond each:
//        # A) when the app started to draw
//        # B) the vsync immediately preceding SF submitting the frame to the h/w
//        # C) timestamp immediately after SF submitted that frame to the h/w
//        #
//        # The difference between the 1st and 3rd timestamp is the frame-latency.
//        # An interesting data is when the frame latency crosses a refresh period
//        # boundary, this can be calculated this way:
//        #
//        # ceil((C - A) / refresh-period)
//        #
//        # (each time the number above changes, we have a "jank").
//        # If this happens a lot during an animation, the animation appears
//        # janky, even if it runs at 60 fps in average.
//        #
//        # We use the special "SurfaceView" window name because the statistics for
//        # the activity's main window are not updated when the main web content is
//        # composited into a SurfaceView.
        ArrayList<Double> timestamps = new ArrayList<>();
        if(results == null || results.length <= 0){
            timestamps.add(null);
            timestamps.add(null);
            return timestamps;
        }

        Double nanosecondsPerSecond = 1e9;
        Double refreshPeriod = Double.valueOf(results[0]) / nanosecondsPerSecond;

//        # If a fence associated with a frame is still pending when we query the
//        # latency data, SurfaceFlinger gives the frame a timestamp of INT64_MAX.
//        # Since we only care about completed frames, we will ignore any timestamps
//        # with this value.
        int pending_fence_timestamp = (1 << 63) - 1;
        for(int i = 1; i < results.length; i++){
            String [] fields = results[i].split("\t");
            if(fields.length != 3){
                continue;
            }
            Double timestamp = null;
            try{
               timestamp = Double.valueOf(fields[1]);
            }catch (NumberFormatException e){
                System.err.println(e);
                continue;
            }
            if(timestamp == pending_fence_timestamp){
                continue;
            }
            timestamp /= nanosecondsPerSecond;
            timestamps.add(timestamp);
        }
        return timestamps;
    }

    @Override
    public boolean start() {
        return false;
    }

    @Override
    public boolean stop() {
        return false;
    }

    public static void main(String[] args) {
        Device device = new Device("localhost", 5037, "21effc3a");
        String apk = "com.happyelements.AndroidAnimal";
        device.startApk(apk);
        FpsMonitor fpsMonitor = new FpsMonitor(device, apk);
        fpsMonitor.getFps();
    }
}
