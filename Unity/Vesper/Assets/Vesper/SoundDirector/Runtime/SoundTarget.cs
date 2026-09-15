using System;
using UnityEngine;

namespace Vesper.SoundDirector {
    [DisallowMultipleComponent]
    public sealed class SoundTarget : MonoBehaviour {
        [HideInInspector] public string id;
        [TextArea] public string description;
        [Range(2, 150)] public float suggestedRadius = 30;
        void Reset() { id = Guid.NewGuid().ToString("N"); description = gameObject.name; }
        void OnDrawGizmosSelected() {
            Gizmos.color = new Color(.25f, .8f, .72f, .65f);
            Gizmos.DrawWireSphere(transform.position, suggestedRadius);
            Gizmos.DrawSphere(transform.position, .35f);
        }
    }
}
