using UnityEngine;
using System.Collections;
using System.Collections.Generic;

//Generates a dataset of labeled images with bounding boxes using the GameObjects in the objects array

public class RandomMover : MonoBehaviour {
	public GameObject[] objects;
	public bool rotateY = true;
	public bool teleport = true;

	public int minX = -20;
	public int maxX = 20;
	public int minY = -5;
	public int maxY = 2;
	public int minZ = -30;
	public int maxZ = 0;

	void Update(){
		foreach (GameObject obj in objects) {
			if (teleport) {
				obj.transform.position = new Vector3 (Random.Range (minX, maxX)
					, Random.Range (minY, maxY)
					, Random.Range (minZ, maxZ));
			}
			obj.transform.Rotate (new Vector3 (0, rotateY ? Random.Range (0, 360) : 0, 0));
		}
	}
}