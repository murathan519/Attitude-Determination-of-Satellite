using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Meteor : MonoBehaviour
{
    public GameObject meteor;
    public GameObject moon;

    public float a = 2.5f;
    public float e = 1.5f;
    public float inclination = 0.0f;
    
    private float unit = 1737.0f;
    private double G_real = 6.6743e-20;
    private double M = 7.342e22;

    private float rp;
    private float T;
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
        T = 10;
        rp = a * (e - 1);
        F = rp + a;
        inclination_radians = inclination * Mathf.Deg2Rad;

        float theta_max = Mathf.Acos(-1 / e);
        theta_radians = theta_max;

        GameObject trailObject = new GameObject("MeteorTrail");
        trailRenderer = trailObject.AddComponent<LineRenderer>();
        trailRenderer.startWidth = 0.02f;
        trailRenderer.endWidth = 0.02f;
        trailRenderer.material = new Material(Shader.Find("Sprites/Default"));
        trailRenderer.startColor = Color.red;
        trailRenderer.endColor = Color.red;
        trailRenderer.positionCount = 0;
    }

    void FixedUpdate()
    {
        float theta_max = Mathf.Acos(-1 / e);
        theta_radians -= (2 * Mathf.PI / T) * Time.deltaTime;
        if (theta_radians < -theta_max)
        {
            Destroy(meteor);
            return;
        }

        float r = a * (e * e - 1) / (1 + e * Mathf.Cos(theta_radians));

        float x_meteor = -a * (e + Mathf.Cos(theta_radians)) / (1 + e * Mathf.Cos(theta_radians)) + F;
        float y_meteor = r * Mathf.Sin(theta_radians);
        float z_meteor = 0;

        float x_inclined = x_meteor;
        float y_inclined = y_meteor * Mathf.Cos(inclination_radians) - z_meteor * Mathf.Sin(inclination_radians);
        float z_inclined = y_meteor * Mathf.Sin(inclination_radians) + z_meteor * Mathf.Cos(inclination_radians);

        Vector3 moonPosition = moon.transform.position;
        Vector3 meteorPosition = new Vector3(x_inclined, z_inclined, y_inclined);
        meteor.transform.position = moonPosition + meteorPosition;

        Vector3 cameraDirection = moonPosition - meteor.transform.position;
        meteor.transform.rotation = Quaternion.LookRotation(cameraDirection);

        Debug.DrawRay(moonPosition, (meteor.transform.position - moonPosition), Color.red);
        UpdateTrail(meteor.transform.position);
    }

    void UpdateTrail(Vector3 newPosition)
    {
        trailPositions.Add(newPosition);
        trailRenderer.positionCount = trailPositions.Count;
        trailRenderer.SetPositions(trailPositions.ToArray());
    }
}