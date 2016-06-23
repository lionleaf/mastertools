using UnityEngine;
using System.Collections;

public class LightSwitch : MonoBehaviour {

	// Use this for initialization
	void Start () {
	
	}
	
	// Update is called once per frame
	void Update () {
		Light light = GetComponent<Light> ();
		int random = Random.Range (0, 10);
		if (random < 1) {
			light.intensity = 0;
		} else {
			light.intensity = 1;
		}
	}
}
