using UnityEngine;
using TMPro;
using UnityEngine.UI;

public class VirtualMoon : MonoBehaviour
{
    public GameObject moon;
    public Camera camera;
    public GameObject textPrefab;
    public GameObject indicatorPrefab;
    public TMP_InputField coordinateInput;
    public Button enterButton;

    private GameObject currentIndicator; 
    private float rotationSpeed = 0.0f;
    private int longitudeLines = 12;
    private int latitudeLines = 19;
    private int lineResolution = 100;
    private float radius = 0.5f;

    private LineRenderer[] longitudeRenderers;
    private TextMeshPro[] longitudeTexts;
    private LineRenderer[] latitudeRenderers;
    private TextMeshPro[] latitudeTexts;

    void Start()
    {
        transform.position = new Vector3(1000f, 0f, 1000f);

        enterButton.onClick.AddListener(PlaceIndicator);
        
        longitudeRenderers = new LineRenderer[longitudeLines];
        longitudeTexts = new TextMeshPro[longitudeLines];
        latitudeRenderers = new LineRenderer[latitudeLines];
        latitudeTexts = new TextMeshPro[latitudeLines];

        DrawLongitudeLines();
        CreateLongitudeTexts();
        DrawLatitudeLines();
        CreateLatitudeTexts();
    }

    void Update()
    {
        transform.Rotate(Vector3.up, rotationSpeed * Time.deltaTime);

        UpdateLongitudeLines();
        UpdateLongitudeTexts();
        UpdateLatitudeLines();
        UpdateLatitudeTexts();
    }

    void PlaceIndicator()
    {
        string inputText = coordinateInput.text;
        string[] coordinates = inputText.Split(' ');

        if (coordinates.Length == 2 &&
            float.TryParse(coordinates[0], System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float latitude) &&
            float.TryParse(coordinates[1], System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float longitude))
        {
            if (currentIndicator != null)
            {
                Destroy(currentIndicator);
            }

            float moonRotationY = moon.transform.rotation.eulerAngles.y; 
            float correctedLongitude = longitude - moonRotationY;

            float x = radius * Mathf.Cos(latitude * Mathf.Deg2Rad) * Mathf.Cos(correctedLongitude * Mathf.Deg2Rad);
            float y = radius * Mathf.Sin(latitude * Mathf.Deg2Rad);
            float z = radius * Mathf.Cos(latitude * Mathf.Deg2Rad) * Mathf.Sin(correctedLongitude * Mathf.Deg2Rad);

            Vector3 indicatorPosition = new Vector3(x, y, z) + moon.transform.position;
            Quaternion indicatorRotation = Quaternion.LookRotation(indicatorPosition - moon.transform.position);

            currentIndicator = Instantiate(indicatorPrefab, indicatorPosition, indicatorRotation);
            currentIndicator.transform.SetParent(moon.transform);
        }
    }

    void DrawLongitudeLines()
    {
        for (int i = 0; i < longitudeLines; i++)
        {
            float angle = i * 30f;
            GameObject lineObj = new GameObject($"Longitude_{i}");
            lineObj.transform.SetParent(moon.transform);
            
            LineRenderer lineRenderer = lineObj.AddComponent<LineRenderer>();
            lineRenderer.startWidth = 0.001f;
            lineRenderer.endWidth = 0.001f;
            lineRenderer.material = new Material(Shader.Find("Sprites/Default"));
            lineRenderer.startColor = Color.blue;
            lineRenderer.endColor = Color.blue;
            lineRenderer.positionCount = lineResolution;
            longitudeRenderers[i] = lineRenderer;
        }
    }

    void UpdateLongitudeLines()
    {
        for (int i = 0; i < longitudeLines; i++)
        {
            float angle = i * 30f;
            LineRenderer lineRenderer = longitudeRenderers[i];

            lineRenderer.positionCount = lineResolution;

            for (int j = 0; j < lineResolution; j++)
            {
                float theta = Mathf.Lerp(-Mathf.PI / 2, Mathf.PI / 2, (float)j / (lineResolution - 1));
                float x = radius * Mathf.Cos(theta) * Mathf.Cos(angle * Mathf.Deg2Rad);
                float y = radius * Mathf.Sin(theta);
                float z = radius * Mathf.Cos(theta) * Mathf.Sin(angle * Mathf.Deg2Rad);

                Vector3 point = new Vector3(x, y, z);
                Vector3 rotatedPoint = moon.transform.rotation * point;

                lineRenderer.SetPosition(j, rotatedPoint + moon.transform.position);
            }
        }
    }

    void CreateLongitudeTexts()
    {
        for (int i = 0; i < longitudeLines; i++)
        {
            float angle = i * 30f;

            GameObject textObj = Instantiate(textPrefab);
            textObj.transform.SetParent(moon.transform);
            textObj.name = $"LongitudeText_{angle}";

            TextMeshPro textMesh = textObj.GetComponent<TextMeshPro>();
            textMesh.text = $"{angle}°";
            textMesh.fontSize = 3;
            textMesh.color = Color.blue;
            textMesh.alignment = TextAlignmentOptions.Center;

            longitudeTexts[i] = textMesh;
        }
    }

    void UpdateLongitudeTexts()
    {
        for (int i = 0; i < longitudeLines; i++)
        {
            float angle = i * 30f;
            float x = radius * Mathf.Cos(angle * Mathf.Deg2Rad);
            float z = radius * Mathf.Sin(angle * Mathf.Deg2Rad);

            Vector3 localTextPosition = new Vector3(x, 0, z);
            Vector3 rotatedTextPosition = moon.transform.rotation * localTextPosition;
            Vector3 textPosition = rotatedTextPosition + moon.transform.position;

            if (longitudeTexts[i] != null)
            {
                longitudeTexts[i].transform.position = textPosition;
                Vector3 outwardDirection = (textPosition - moon.transform.position).normalized;
                longitudeTexts[i].transform.rotation = Quaternion.LookRotation(-outwardDirection);
                longitudeTexts[i].text = $"{angle}°";
            }
        }
    }

    void DrawLatitudeLines()
    {
        for (int i = 0; i < latitudeLines; i++)
        {
            float latitude = -90f + i * 10f;
            GameObject lineObj = new GameObject($"Latitude_{i}");
            lineObj.transform.SetParent(moon.transform);

            LineRenderer lineRenderer = lineObj.AddComponent<LineRenderer>();
            lineRenderer.startWidth = 0.001f;
            lineRenderer.endWidth = 0.001f;
            lineRenderer.material = new Material(Shader.Find("Sprites/Default"));
            lineRenderer.startColor = Color.green;
            lineRenderer.endColor = Color.green;
            lineRenderer.positionCount = lineResolution;
            latitudeRenderers[i] = lineRenderer;
        }
    }

    void UpdateLatitudeLines()
    {
        for (int i = 0; i < latitudeLines; i++)
        {
            float latitude = -90f + i * 10f;
            LineRenderer lineRenderer = latitudeRenderers[i];

            lineRenderer.positionCount = lineResolution;

            for (int j = 0; j < lineResolution; j++)
            {
                float theta = Mathf.Lerp(0, 360, (float)j / (lineResolution - 1));
                float x = radius * Mathf.Cos(latitude * Mathf.Deg2Rad) * Mathf.Cos(theta * Mathf.Deg2Rad);
                float y = radius * Mathf.Sin(latitude * Mathf.Deg2Rad);
                float z = radius * Mathf.Cos(latitude * Mathf.Deg2Rad) * Mathf.Sin(theta * Mathf.Deg2Rad);

                Vector3 point = new Vector3(x, y, z);
                Vector3 rotatedPoint = moon.transform.rotation * point;

                lineRenderer.SetPosition(j, rotatedPoint + moon.transform.position);
            }
        }
    }

    void CreateLatitudeTexts()
    {
        for (int i = 0; i < latitudeLines; i++)
        {
            float latitude = -90f + i * 10f;
            GameObject textObj = Instantiate(textPrefab);
            textObj.transform.SetParent(moon.transform);
            textObj.name = $"LatitudeText_{latitude}";

            TextMeshPro textMesh = textObj.GetComponent<TextMeshPro>();
            textMesh.text = $"{(latitude > 0 ? "+" : "")}{latitude}°";
            textMesh.fontSize = 3;
            textMesh.color = Color.green;
            textMesh.alignment = TextAlignmentOptions.Center;

            latitudeTexts[i] = textMesh;
        }
    }

    void UpdateLatitudeTexts()
    {
        Vector3 cameraDirection = (camera.transform.position - moon.transform.position).normalized;

        for (int i = 0; i < latitudeLines; i++)
        {
            float latitude = -90f + i * 10f;

            Vector3 idealTextPosition = moon.transform.position + cameraDirection * radius * Mathf.Cos(latitude * Mathf.Deg2Rad);
            
            float x = idealTextPosition.x;
            float y = radius * Mathf.Sin(latitude * Mathf.Deg2Rad);
            float z = idealTextPosition.z;

            Vector3 textPosition = new Vector3(x, y, z);

            if (latitudeTexts[i] != null)
            {
                latitudeTexts[i].transform.position = textPosition;
                Vector3 outwardDirection = (textPosition - moon.transform.position).normalized;
                latitudeTexts[i].transform.rotation = Quaternion.LookRotation(-outwardDirection);
            }
        }
    }
}