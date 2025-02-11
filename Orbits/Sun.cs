using UnityEngine;

public class Sun : MonoBehaviour
{
    public GameObject sun;
    private Vector3 fixedPosition = Vector3.zero;

    void Start()
    {
        transform.position = fixedPosition;
    }

    void Update()
    {
        transform.position = fixedPosition;
    }

    void OnValidate()
    {
        transform.position = fixedPosition;
    }
}
