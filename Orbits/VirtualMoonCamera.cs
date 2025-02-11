using UnityEngine;

public class VirtualMoonCamera : MonoBehaviour
{
    void Start()
    {
        transform.position = new Vector3(998.7f, 0f, 1000f);
        transform.rotation = Quaternion.Euler(0f, 90f, 0f);
    }
}
