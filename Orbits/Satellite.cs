using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Satellite : MonoBehaviour
{
    public GameObject satellite;
    public GameObject moon;

    public float a = 2.5f;
    public float e = 0.5f;   
    public float inclination = 0.0f;
    public float theta_degrees = 0.0f; 

    private float unit = 1737.0f;
    private double G_real = 6.6743e-20;
    private double M = 7.342e22;

    private float T; 
    private float b; 
    private float F;
    private double G; 
    private double mu; 
    private float theta_radians;
    private float inclination_radians;

    private LineRenderer trailRenderer;
    private List<Vector3> trailPositions = new List<Vector3>();

    void Start()
    {
        G = G_real / Mathf.Pow(unit, 3);
        mu = G * M;
        T = 10;  //2848 
        b = a * Mathf.Sqrt(1 - e * e);
        F = a * e;  
        theta_radians = theta_degrees * Mathf.Deg2Rad;
        inclination_radians = inclination * Mathf.Deg2Rad;

        trailRenderer = satellite.AddComponent<LineRenderer>();
        trailRenderer.startWidth = 0.02f;
        trailRenderer.endWidth = 0.02f;
        trailRenderer.material = new Material(Shader.Find("Sprites/Default"));
        trailRenderer.startColor = Color.yellow;
        trailRenderer.endColor = Color.yellow;
        trailRenderer.positionCount = 0;
    }

    void FixedUpdate()
    {
        theta_radians += (2 * Mathf.PI / T) * Time.deltaTime;
        
        if (theta_radians > 2 * Mathf.PI)
        {
            theta_radians -= 2 * Mathf.PI;
        }

        float x_satellite = a * (e + Mathf.Cos(theta_radians)) / (1 + e * Mathf.Cos(theta_radians)) + F;
        float y_satellite = (b * Mathf.Sqrt(1 - e * e) * Mathf.Sin(theta_radians)) / (1 + e * Mathf.Cos(theta_radians));
        float z_satellite = 0;

        float x_inclined = x_satellite;
        float y_inclined = y_satellite * Mathf.Cos(inclination_radians) - z_satellite * Mathf.Sin(inclination_radians);
        float z_inclined = y_satellite * Mathf.Sin(inclination_radians) + z_satellite * Mathf.Cos(inclination_radians);

        Vector3 moonPosition = moon.transform.position;
        Vector3 satellitePosition = new Vector3(x_inclined, z_inclined, y_inclined);
        satellite.transform.position = moonPosition + satellitePosition;

        Vector3 cameraDirection = moonPosition - satellite.transform.position;
        satellite.transform.rotation = Quaternion.LookRotation(cameraDirection);

        Debug.DrawRay(moonPosition, (satellite.transform.position - moonPosition), Color.yellow);
        UpdateTrail(satellite.transform.position);
    }

    void UpdateTrail(Vector3 newPosition)
    {
        trailPositions.Add(newPosition);
        trailRenderer.positionCount = trailPositions.Count;
        trailRenderer.SetPositions(trailPositions.ToArray());
    }
}
