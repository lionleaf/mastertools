using UnityEngine;
using System.Collections;

public class Rotator : MonoBehaviour {

	public bool rotateAroundX;
	public bool rotateAroundY;
	public bool rotateAroundZ;

	void Update () {
		float xRotation = 0;
		float yRotation = 0;
		float zRotation = 0;

		if (rotateAroundX) {
			xRotation = Random.Range (0, 360);
		}

		if (rotateAroundY) {
			yRotation = Random.Range (0, 360);
		}

		if (rotateAroundZ) {
			zRotation = Random.Range (0, 360);
		}

		transform.Rotate (xRotation, yRotation, zRotation);
	}
}
