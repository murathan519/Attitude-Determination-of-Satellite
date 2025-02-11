using System;
using System.IO;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Collections.Concurrent;
using UnityEngine;

public class TCP : MonoBehaviour
{
    public GameObject moon;
    public GameObject earth;
    
    public GameObject moon_light;
    public GameObject earth_light;
    private Vector3 fixedPosition = Vector3.zero;

    private int unit = 1737;

    private string host = "127.0.0.1";
    private int port = 12345;

    private TcpClient client;
    private StreamReader reader;
    private Thread clientThread;
    private bool isRunning = true;

    private ConcurrentQueue<string> telemetryQueue = new ConcurrentQueue<string>();

    void Start()
    {
        earth_light.transform.position = fixedPosition;
        moon_light.transform.position = fixedPosition;

        try
        {
            client = new TcpClient(host, port);
            reader = new StreamReader(client.GetStream(), Encoding.UTF8);
            Debug.Log($"Connected to the receiver: {host}:{port}");

            clientThread = new Thread(TCPReceiver);
            clientThread.Start();
        }
        catch (Exception e)
        {
            Debug.LogError($"Connection error: {e.Message}");
        }
    }

    void TCPReceiver()
    {
        try
        {
            while (isRunning)
            {
                if (reader != null)
                {
                    string telemetryData = reader.ReadLine();
                    if (!string.IsNullOrEmpty(telemetryData))
                    {
                        telemetryQueue.Enqueue(telemetryData);
                        Debug.Log($"Enqueued Telemetry Data: {telemetryData}");
                    }
                    else
                    {
                        Debug.Log("Empty data received.");
                    }
                }
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"Error in TCP thread: {e.Message}");
        }
    }

    void FixedUpdate()
    {
        earth_light.transform.position = fixedPosition;
        moon_light.transform.position = fixedPosition;

        while (telemetryQueue.TryDequeue(out string telemetryData))
        {
            try
            {
                string[] data = telemetryData.Split(",");
                if (data.Length == 12)
                {
                    float x_earth = float.Parse(data[0],  System.Globalization.CultureInfo.InvariantCulture);
                    float z_earth = float.Parse(data[1],  System.Globalization.CultureInfo.InvariantCulture);
                    float y_earth = float.Parse(data[2],  System.Globalization.CultureInfo.InvariantCulture);

                    float r_earth = float.Parse(data[3],  System.Globalization.CultureInfo.InvariantCulture);
                    float w_earth = float.Parse(data[4],  System.Globalization.CultureInfo.InvariantCulture);
                    float p_earth = float.Parse(data[5],  System.Globalization.CultureInfo.InvariantCulture);

                    float x_moon = float.Parse(data[6],  System.Globalization.CultureInfo.InvariantCulture);
                    float z_moon = float.Parse(data[7],  System.Globalization.CultureInfo.InvariantCulture);
                    float y_moon = float.Parse(data[8],  System.Globalization.CultureInfo.InvariantCulture);

                    float r_moon = float.Parse(data[9],  System.Globalization.CultureInfo.InvariantCulture);
                    float w_moon = float.Parse(data[10], System.Globalization.CultureInfo.InvariantCulture);
                    float p_moon = float.Parse(data[11], System.Globalization.CultureInfo.InvariantCulture);

                    x_earth /= unit;
                    y_earth /= unit;
                    z_earth /= unit;

                    x_moon /= unit;
                    y_moon /= unit;
                    z_moon /= unit;
                    
                    Vector3 targetEarthPosition = new Vector3(x_earth, y_earth, z_earth);
                    Vector3 targetMoonPosition = new Vector3(x_moon, y_moon, z_moon);
                    Quaternion targetEarthRotation = Quaternion.Euler(r_earth, p_earth, w_earth);
                    Quaternion targetMoonRotation = Quaternion.Euler(r_moon, p_moon, w_moon);

                    earth.transform.position = Vector3.Lerp(earth.transform.position, targetEarthPosition, 0.1f);
                    moon.transform.position = Vector3.Lerp(moon.transform.position, targetMoonPosition, 0.1f);
                    earth.transform.rotation = Quaternion.Slerp(earth.transform.rotation, targetEarthRotation, 0.1f);
                    moon.transform.rotation = Quaternion.Slerp(moon.transform.rotation, targetMoonRotation, 0.1f);
                    
                    /*
                    earth.transform.position = new Vector3(x_earth, y_earth, z_earth);
                    earth.transform.rotation = Quaternion.Euler(r_earth, p_earth, w_earth);
                    moon.transform.position = new Vector3(x_moon, y_moon, z_moon);
                    moon.transform.rotation = Quaternion.Euler(r_moon, p_moon, w_moon);
                    */

                    Vector3 earthPosition = new Vector3(x_earth, y_earth, z_earth);
                    Vector3 directionToEarth = earthPosition.normalized; 
                    Vector3 moonPosition = new Vector3(x_moon, y_moon, z_moon);
                    Vector3 directionToMoon = moonPosition.normalized; 

                    earth_light.transform.rotation = Quaternion.LookRotation(directionToEarth);
                    moon_light.transform.rotation = Quaternion.LookRotation(directionToMoon);

                    
                    Ray rayToEarth = new Ray(earthPosition, (moonPosition - earthPosition).normalized);
                    Debug.DrawRay(earthPosition, (moonPosition - earthPosition), Color.red);
                    
                    Ray rayToSun = new Ray(fixedPosition, (moonPosition - fixedPosition).normalized);
                    Debug.DrawRay(fixedPosition, (moonPosition - fixedPosition), Color.white);
                }
                else
                {
                    Debug.LogWarning($"Unexpected data format: {telemetryData}");
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"Error while processing data: {e.Message}. Raw data: {telemetryData}");
            }
        }
    }

    void OnApplicationQuit()
    {
        isRunning = false;

        if (clientThread != null && clientThread.IsAlive)
        {
            clientThread.Join();
        }

        if (reader != null) reader.Close();
        if (client != null) client.Close();

        Debug.Log("TCP connection is ended.");
    }
}